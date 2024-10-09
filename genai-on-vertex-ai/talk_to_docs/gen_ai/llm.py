# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This module contains functionalities to manage and execute language model (LLM) interactions,
document retrieval, response generation, and logging within a conversational AI context. It integrates
several components for handling complex AI tasks, including generating contextual responses,
managing state across conversational turns, and logging interactions for analysis.

The module is structured to process conversations using document retrievers, respond to user queries,
and log conversation states and interactions to BigQuery for further analysis. It uses dependency injection
to manage dependencies and settings, facilitating a flexible and decoupled design.

Functions:
    get_total_count(question, selected_context, previous_rounds, final_round_statement): Calculates the total 
    token count.
    generate_response_react(conversation): Handles the generation of responses in a reactive conversation cycle.
    respond(conversation, member_info): Processes a full conversational round, updating the conversation state.
    respond_api(question, member_context_full): Provides an API-like interface to handle incoming queries and 
    generate responses.

Classes:
    None

Dependencies:
    - gen_ai.common: Provides common utilities and configurations.
    - langchain: Used for language model operations.
    - json5: Used for JSON parsing.
"""

import uuid
from timeit import default_timer
from typing import Any

import json5
from dependency_injector.wiring import inject
from langchain.chains import LLMChain

from gen_ai.common.argo_logger import create_log_snapshot
from gen_ai.common.bq_utils import load_data_to_bq
from gen_ai.common.common import merge_outputs, remove_duplicates
from gen_ai.common.exponential_retry import concurrent_best_reduce, timeout_llm_call
from gen_ai.common.ioc_container import Container
from gen_ai.common.memorystore_utils import serialize_previous_conversation
from gen_ai.common.react_utils import filter_non_relevant_previous_conversations, get_confidence_score
from gen_ai.common.retriever import perform_retrieve_round, retrieve_initial_documents
from gen_ai.common.statefullness import resolve_and_enrich, serialize_response
from gen_ai.custom_client_functions import fill_query_state_with_doc_attributes, generate_contexts_from_docs
from gen_ai.deploy.model import Conversation, PersonalizedData, QueryState, transform_to_dictionary


def get_total_count(question: str, selected_context: str, previous_rounds: str, final_round_statement: str) -> str:
    """
    Calculates the total token count for a given context setup in a conversational AI environment.

    This function constructs a full prompt from various components of a conversation including the main question,
    selected context from documents, any preceding rounds of conversation, and a final statement if it is the last
    round. It then calculates the total number of tokens this combined prompt would take up when processed by a
    language model, assisting in managing and optimizing language model input size constraints.

    Args:
        question (str): The primary question being addressed in the conversation.
        selected_context (str): The context selected from documents relevant to the question.
        previous_rounds (str): Accumulated context from previous rounds of the conversation, maintaining the
                               continuity necessary for the language model.
        final_round_statement (str): A concluding statement used in the final round of the conversation, often
                                     summarizing or closing the discussion.

    Returns:
        str: The total token count as a string, representing the sum of tokens from all parts of the constructed prompt.

    Example:
        >>> question = "What are the benefits of renewable energy?"
        >>> selected_context = "Renewable energy, often referred to as clean energy, comes from natural sources..."
        >>> previous_rounds = "Previous discussions included solar and wind energy."
        >>> final_round_statement = "This concludes our discussion on renewable energy."
        >>> token_count = get_total_count(question, selected_context, previous_rounds, final_round_statement)
        >>> print(token_count)
        '120'  # Example output, the actual number depends on the tokenization process.

    Note:
        The token count helps in managing inputs to language models, especially when dealing with models that have
        a maximum token input limit. Ensuring that the prompt does not exceed this limit is crucial for
        effective processing.
    """
    react_chain: LLMChain = Container.react_chain
    prompt = (
        f"{react_chain().prompt.template}\n{question}\n{selected_context}\n{previous_rounds}\n{final_round_statement}\n"
    )
    query_tokens = Container.token_counter().get_num_tokens_from_string(prompt)
    return query_tokens


@concurrent_best_reduce(num_calls=Container.config.get("parallel_main_llm_calls", 1))
@timeout_llm_call(timeout=Container.config.get("parallel_main_llm_timeout", 20))
def perform_main_llm_call(
    react_chain: Any,
    question: str,
    previous_context: str,
    selected_context: str,
    previous_rounds: list[dict],
    round_number: int,
    final_round_statement: str,
    post_filtered_docs: list,
) -> tuple[dict[str, Any], float]:
    """Performs a main LLM (Large Language Model) call to generate an answer to a question.

    This function orchestrates the core LLM interaction, incorporating retry mechanisms for JSON parsing
    and confidence scoring. It leverages the `@concurrent_best_reduce` decorator for potential concurrent calls.

    Args:
        react_chain: The LLM chain for generating the initial answer.
        question: The question to be answered.
        previous_context: Context from previous interactions or rounds.
        selected_context: The specific context selected for this call.
        previous_rounds: History of previous question-answer rounds.
        round_number: The current round number.
        final_round_statement: A statement for the final round, if applicable.
        post_filtered_docs: List of documents filtered post-retrieval (may be empty).

    Returns:
        Tuple[Dict[str, Any], float]: A tuple containing:
            - The LLM output as a dictionary (with keys like "answer", "plan_and_summaries", etc.).
            - The confidence score of the answer.
    """
    llm_start_time = default_timer()

    output_raw = react_chain().run(
        include_run_info=True,
        return_only_outputs=False,
        question=question,
        previous_conversation=previous_context,
        context=selected_context,
        previous_rounds=previous_rounds,
        round_number=round_number,
        final_round_statement=final_round_statement,
    )

    llm_end_time = default_timer()
    Container.logger().info(f"Generating main LLM answer took {llm_end_time - llm_start_time} seconds")
    default_error_response = (
        {
            "answer": "I was not able to answer this question",
            "plan_and_summaries": "",
            "context_used": "[]",
            "additional_information_to_retrieve": "",
        },
        0,
        False
    )
    try:
        output_raw = output_raw.replace("`json", "").replace("`", "")
        output = json5.loads(output_raw)
    except Exception as e:  # pylint: disable=W0718
        Container.logger().info(msg="Crashed before correct chain")
        Container.logger().info(msg=str(e))
        return default_error_response

    if "answer" not in output or (
        len(post_filtered_docs) == 0 and not output.get("additional_information_to_retrieve", None)
    ):
        return default_error_response

    if Container.config.get("separate_confidence_score", True):
        confidence = get_confidence_score(question, output["answer"])
    else:
        try:
            confidence = output.get("confidence_score", 0)
            confidence = int(confidence)
        except ValueError:
            print("failed to convert {confidence} to integer")
            print(f"{confidence}")
            confidence = 0

    return output, confidence, True  # return output and confidence


@inject
def generate_response_react(conversation: Conversation) -> tuple[Conversation, list[dict[str, Any]]]:
    """
    Generates responses within a conversational cycle, considering various conversation states and document contexts.

    This function orchestrates the response generation process by managing document retrieval,
    context generation, and reaction to queries based on the ongoing conversation state. It processes
    the conversation through various stages, utilizing LLM chains and custom utilities to refine the
    conversation context and generate appropriate responses.

    Args:
        conversation (Conversation): The current conversation object containing all exchanges and context.

    Returns:
        tuple[Conversation, list[dict[str, Any]]]: Updated conversation object with the new exchange added,
        and a list of log snapshots detailing each step of the conversation processing.

    Raises:
        Exception: If there is any issue in the processing steps, including document retrieval,
        context generation, or response handling.
    """
    react_chain: LLMChain = Container.react_chain
    vector_indices: dict = Container.vector_indices
    config: dict = Container.config

    document_retriever_name = config.get("document_retriever")
    member_info = conversation.member_info

    query_state = conversation.exchanges[-1]
    question = query_state.question

    query_state.react_rounds = []
    log_snapshots = []
    round_number = len(query_state.react_rounds) + 1
    if len(conversation.exchanges) > 1 and config.get("api_mode") == "stateful":
        number_of_previous_conversations = config.get("previous_conversations_number")
        previous_conversations = conversation.exchanges[:-1][:number_of_previous_conversations]
        relevant_previous_conversations = filter_non_relevant_previous_conversations(previous_conversations, question)
        previous_context = serialize_previous_conversation(relevant_previous_conversations[::-1])
        previous_questions = [x.question for x in relevant_previous_conversations]
    else:
        previous_context = ""
        previous_questions = None
        prev_pre_filtered_docs, prev_post_filtered_docs = [], []

    pre_filtered_docs, post_filtered_docs = retrieve_initial_documents(
        round_number, question, vector_indices, document_retriever_name, member_info
    )

    if previous_questions:
        concatenated_with_previous = previous_questions + [question]
        prev_pre_filtered_docs, prev_post_filtered_docs = perform_retrieve_round(
            -1, concatenated_with_previous, vector_indices, document_retriever_name, member_info
        )
        pre_filtered_docs = prev_pre_filtered_docs + pre_filtered_docs
        pre_filtered_docs = remove_duplicates(pre_filtered_docs)
        post_filtered_docs = prev_post_filtered_docs + post_filtered_docs

    post_filtered_docs = remove_duplicates(post_filtered_docs)
    contexts = generate_contexts_from_docs(post_filtered_docs, query_state)

    final_round_statement = ""
    max_rounds = config.get("max_rounds", 3)
    previous_rounds = config.get("first_round_statement", "")

    while len(query_state.react_rounds) < max_rounds:
        start_time = default_timer()
        if query_state.additional_information_to_retrieve:
            pre_filtered_missing_information_documents, post_filtered_missing_information_documents = (
                perform_retrieve_round(
                    round_number,
                    [query_state.additional_information_to_retrieve],
                    vector_indices,
                    document_retriever_name,
                    member_info,
                )
            )
            if post_filtered_missing_information_documents:
                post_filtered_docs = post_filtered_missing_information_documents + post_filtered_docs

            if pre_filtered_missing_information_documents:
                pre_filtered_docs = pre_filtered_missing_information_documents + pre_filtered_docs

            post_filtered_docs = remove_duplicates(post_filtered_docs)
            contexts = generate_contexts_from_docs(post_filtered_docs, query_state)

        round_number = len(query_state.react_rounds) + 1
        if round_number == max_rounds:
            final_round_statement = config.get("final_round_statement", "")

        round_outputs = []
        for selected_context in contexts:
            output, confidence, _ = perform_main_llm_call(
                react_chain,
                question,
                previous_context,
                selected_context,
                previous_rounds,
                round_number,
                final_round_statement,
                post_filtered_docs,
            )
            round_outputs.append((output, confidence))

        end_time = default_timer()
        query_state.time_taken = end_time - start_time
        output, confidence, index = merge_outputs(round_outputs)
        selected_context = contexts[index]

        if "context_used" not in output:
            output["context_used"] = ""
        react_snapshot = {
            "round_number": round_number,
            "plan_and_summaries": output["plan_and_summaries"],
            "answer": output["answer"],
            "confidence_score": confidence,
            "context_used": output["context_used"],
            "additional_information_to_retrieve": output["additional_information_to_retrieve"],
        }
        query_state.react_rounds.append(react_snapshot)
        previous_rounds = json5.dumps(query_state.react_rounds, indent=4)

        query_state.additional_information_to_retrieve = output.get("additional_information_to_retrieve", None)

        log_snapshot = create_log_snapshot(
            react_snapshot,
            pre_filtered_docs,
            post_filtered_docs,
            query_state.additional_information_to_retrieve,
            query_state.time_taken,
        )
        log_snapshots.append(log_snapshot)
        Container.logger().info(msg="-----------------------------------")
        Container.logger().info(msg="Additional information to retrieve:")
        Container.logger().info(msg=query_state.additional_information_to_retrieve)
        Container.logger().info(msg="-----------------------------------")
        Container.logger().info(msg="Confidence:")
        Container.logger().info(msg=confidence)
        Container.logger().info(msg="------------------------")
        Container.logger().info(msg=react_snapshot)
        if not query_state.additional_information_to_retrieve:
            break

        if confidence >= 5:
            break

    conversation.round_numder = round_number
    query_state.answer = output["answer"]
    query_state.relevant_context = output["context_used"]
    query_state.all_sections_needed = [x[0] for x in query_state.used_articles_with_scores]
    query_state.used_articles_with_scores = None
    query_state.confidence_score = confidence
    query_state, post_filtered_docs = fill_query_state_with_doc_attributes(query_state, post_filtered_docs)
    for x in log_snapshots:
        x["post_filtered_docs_so_far"] = post_filtered_docs

    return conversation, log_snapshots


def respond(conversation: Conversation, member_info: dict) -> Conversation:
    """
    Processes and responds to the latest exchange in a conversation, applying stateful or stateless logic as configured.

    This function updates the conversation based on the latest interaction, employing the configured
    API mode to determine how contextually or independently each message should be handled. It integrates
    various components to enrich the conversation with AI-generated content and logs the results.

    Args:
        conversation (Conversation): The ongoing conversation object to be updated.
        member_info (dict): Additional metadata about the conversation member, used for personalizing responses.

    Returns:
        Conversation: The updated conversation object after processing the latest interaction.

    Raises:
        Exception: If issues arise in conversation processing or during response generation.
    """
    conversation.member_info = member_info
    if conversation.member_info and "set_number" in conversation.member_info:
        conversation.member_info["set_number"] = conversation.member_info["set_number"].lower()
    if conversation.member_info and "session_id" in conversation.member_info:
        conversation.session_id = conversation.member_info["session_id"]
    else:
        conversation.session_id = str(uuid.uuid4())

    api_mode = Container.config.get("api_mode", "stateless")
    statefullness_enabled = api_mode == "stateful"
    if statefullness_enabled:
        if "member_id" not in member_info:
            Container.logger().error("Stateful API is enabled, but no member_id was provided")
            raise ValueError("Member id is not provided for Stateful API and Multi-Turn")
        conversation = resolve_and_enrich(conversation)

    conversation, log_snapshots = generate_response_react(conversation)

    if statefullness_enabled:
        serialize_response(conversation)

    Container.logging_bq_executor().submit(load_data_to_bq, conversation, log_snapshots)

    return conversation


def respond_api(question: str, member_context_full: PersonalizedData | dict[str, str]) -> Conversation:
    """
    Provides an API-like interface to handle and respond to a new question within a conversation context.

    This function initializes a conversation state for a new question, applies the conversational
    logic through `respond`, and returns the updated conversation object. It's designed to be an
    entry point for external systems to interact with the conversational AI logic.

    Args:
        question (str): The question to be processed.
        member_context_full (PersonalizedData): Contextual data about the member, enhancing personalization.

    Returns:
        Conversation: A conversation object containing the initial query and the generated response.

    Raises:
        Exception: If the conversation processing fails at any step.
    """
    if isinstance(member_context_full, PersonalizedData):
        member_context_full = transform_to_dictionary(member_context_full)
    query_state = QueryState(question=question, all_sections_needed=[])
    query_state.original_question = (
        Container.original_question
        if (hasattr(Container, "original_question") and Container.original_question is not None)
        else None
    )
    conversation = Conversation(exchanges=[query_state])
    conversation = respond(conversation, member_context_full)
    return conversation

