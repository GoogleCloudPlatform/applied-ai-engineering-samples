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
This module integrates several functionalities to enhance document processing using language model chains (LLMChain).
It includes functions for scoring documents based on relevancy to a specific query, summarizing documents based on
content relevance, and a combination of both scoring and summarizing. These processes leverage error handling for
JSON outputs and are optimized with concurrency techniques using ThreadPoolExecutor for efficiency.

Functions:
    get_confidence_score(question: str, answer: str) -> int:
        Calculate and return a confidence score for a given question-answer pair.
    score_document(
        doc: Document, index: int, question: str, retriever_scoring_chain: LLMChain, json_corrector_chain: LLMChain) 
        -> Tuple[int, Document]:
        Score a document's relevance to a specific question.
    score_retrieved_documents(docs: List[Document], question: str) -> List[Document]:
        Score a list of documents based on their relevance to a given question.
    summarize_document(
        doc: Document, index: int, question: str, aspect_based_summary_chain: LLMChain, json_corrector_chain: LLMChain) 
        -> Tuple[int, Document]:
        Summarize a document based on a specific question and content.
    summarize_retrieved_documents(docs: List[Document], question: str) -> List[Document]:
        Summarize a list of documents based on a specific question.
    print_doc_summary_and_relevance(docs_and_scores: List[Document]):
        Print summaries and relevance details for a list of documents.
    summarize_and_score_documents(
        docs_and_scores: List[Document], question: str, threshold: int | None = None) -> List[Document]:
        Summarize and score documents based on their relevance to a specific question and filter them by a 
        relevancy score threshold.

Classes:
    None

Dependencies:
    - concurrent.futures for parallel execution
    - json5 for JSON parsing and correction
    - langchain and gen_ai libraries for language model operations and custom utilities
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

import json5
from langchain.chains import LLMChain
from langchain.schema import Document

from gen_ai.common.measure_utils import trace_on
from gen_ai.common.ioc_container import Container
from gen_ai.deploy.model import QueryState

def get_confidence_score(question: str, answer: str) -> int:
    """Calculate confidence score for the given question-answer pair.

    Args:
        question (str): The question for which the confidence score is calculated.
        answer (str): The answer to be scored for confidence.

    Returns:
        int: Confidence score indicating the degree of confidence in the answer.
             It is an integer value ranging from 0 to 100.

    Raises:
        Any errors raised during JSON parsing of the answer scoring result.

    Note:
        This method utilizes an answer scoring chain to evaluate the confidence
        score of the provided answer in response to the given question. If any
        errors occur during the process, a default confidence score of 0 is returned.
    """
    answer_scoring_chain: LLMChain = Container.answer_scoring_chain
    json_corrector_chain: LLMChain = Container.json_corrector_chain

    answer_scoring_raw = answer_scoring_chain().run(question=question, answer=answer)
    try:
        answer_scoring_raw = answer_scoring_raw.replace("```json", "").replace("```", "")
        answer_scoring = json5.loads(answer_scoring_raw)
    except Exception:  # pylint: disable=W0718
        try:
            answer_scoring_raw = json_corrector_chain().run(json=answer_scoring_raw)
            answer_scoring_raw = answer_scoring_raw.replace("```json", "").replace("```", "")
            answer_scoring = json5.loads(answer_scoring_raw)
        except Exception as _:  # pylint: disable=W0718
            print("failed to parse confidence score")
            print(f"{answer_scoring_raw}")
            answer_scoring = {"confidence_score": 0}

    confidence = answer_scoring.get("confidence_score")

    try:
        confidence = int(confidence)
    except ValueError:
        print("failed to convert {confidence} to integer")
        print(f"{answer_scoring_raw}")
        confidence = 0

    return confidence


def score_document(
    doc: Document, index: int, question: str, retriever_scoring_chain: LLMChain, json_corrector_chain: LLMChain
) -> Tuple[int, Document]:
    """
    Scores a single document for its relevance to a given question using a retriever scoring chain and corrects
    the output using a JSON corrector chain if necessary.

    This method attempts to score a document's relevance to a specific question by running the document's content
    and the question through a retriever scoring chain. If the output from the retriever scoring chain is not valid
    JSON, the method attempts to correct it using a JSON corrector chain before parsing it again. The method returns
    the document's index, its relevancy score, and the reasoning behind the score.

    Parameters:
    - doc (Document): The Document object to be scored. The Document object must have a `page_content` attribute
      containing the text to be analyzed.
    - index (int): The index of the document in the original list of documents. Used to match the score and reasoning
      back to the correct document.
    - question (str): The question string against which the document's relevance is being scored.
    - retriever_scoring_chain (LLMChain): The Language Model Chain used for scoring the document's relevance to the
      question.
    - json_corrector_chain (LLMChain): The Language Model Chain used for correcting the output from the retriever
      scoring chain if it is not valid JSON.

    Returns:
    - Tuple[int, Document]: A tuple containing two elements:
        1. The index of the document (int).
        2. The Document with inserted metadata - "relevancy_score" and "relevancy_reasoning".

    The method first tries to parse the output from the retriever scoring chain. If the output is not valid JSON,
    it catches the exception, runs the output through the JSON corrector chain, and attempts to parse it again. If
    any part of this process fails, it sets the relevancy score to 0 and prints an error message along with the raw
    output for debugging purposes.

    Note:
    - The `retriever_scoring_chain.run` method is expected to return a string that can be parsed into JSON containing
      at least the keys `relevancy_score` and `relevancy_reasoning`.
    - It is assumed that the `json_corrector_chain.run` method can correct minor issues in the string to make it valid
      JSON.
    - This method does not catch all exceptions explicitly. In case of an unexpected error, it defaults the relevancy
      score to 0 and prints the raw output for inspection.
    """
    use_relevancy_score = Container.config.get("use_relevancy_score", False)
    relevancy_score = 0
    relevancy_reasoning = "The text could not be scored"

    if use_relevancy_score:
        output = {}
        doc_content = doc.page_content if Container.config.get("use_full_documents", False) else doc.metadata["summary"]
        try:
            output_raw = retriever_scoring_chain.run(retrieved_doc=doc_content, question=question)
            try:
                output_raw = output_raw.replace("```json", "").replace("```", "")
                output = json5.loads(output_raw)
            except Exception:  # pylint: disable=W0718
                json_output = json_corrector_chain.run(json=output_raw)
                json_output = json_output.replace("```json", "").replace("```", "")
                output = json5.loads(json_output)
            relevancy_score = int(output["relevancy_score"])
            relevancy_reasoning = output["relevancy_reasoning"]
        except Exception as e:  # pylint: disable=W0718
            print("Error in parsing the document for relevancy score")
            print(str(e))
            relevancy_score = 0
            relevancy_reasoning = "Failed to assign relevant score"

    doc.metadata["relevancy_score"] = relevancy_score
    doc.metadata["relevancy_reasoning"] = relevancy_reasoning

    return index, doc


@trace_on("Only scoring documents", measure_time=True)
def score_retrieved_documents(docs: List[Document], question: str) -> List[Document]:
    """
    Scores each document in a list of documents based on how relevant they are to a given question.

    This method uses a retriever scoring chain and a JSON corrector chain to evaluate each document. It executes
    the scoring in parallel using a ThreadPoolExecutor, which can speed up the processing time when dealing with
    a large number of documents. Each document is scored, and a relevancy reasoning is provided along with the score.

    Parameters:
    - docs (List[Document]): A list of Document objects to be scored. Each Document object should contain the data
      necessary for scoring against the given question.
    - question (str): The question string against which the documents' relevance is to be scored.

    Returns:
    - List[Tuple[int, str]]: A list of tuples, where each tuple contains two elements:
        1. An integer score representing the document's relevance to the question.
        2. A Document with updated metadata.

    The method initializes two chains, `retriever_scoring_chain` and `json_corrector_chain`, which are used for scoring
    the documents. The scoring process for each document is submitted to a ThreadPoolExecutor for parallel execution.
    As each scoring task completes, the result, which includes the document's index in the original list, its score,
    and the relevancy reasoning, is used to update the `scores_and_reasonings` list at the corresponding index.

    Note:
    - The scoring algorithm and the rationale for the relevancy reasoning depend on the implementations of the
      `score_document` function, `retriever_scoring_chain`, and `json_corrector_chain`.
    - This method assumes that `Container.retriever_scoring_chain()` and `Container.json_corrector_chain()` are
      accessible and properly initialized before calling this method.
    """
    retriever_scoring_chain = Container.retriever_scoring_chain()
    json_corrector_chain = Container.json_corrector_chain()
    scored_documents = [" "] * len(docs)

    with ThreadPoolExecutor() as executor:
        future_to_doc = {
            executor.submit(score_document, doc, i, question, retriever_scoring_chain, json_corrector_chain): doc
            for i, doc in enumerate(docs)
        }

        for future in as_completed(future_to_doc):
            index, doc = future.result()
            scored_documents[index] = doc

    return scored_documents


def summarize_document(
    doc: Document, index: int, question: str, aspect_based_summary_chain: LLMChain, json_corrector_chain: LLMChain
) -> Tuple[int, Document]:
    """
    Summarize a document based on a specific question using an aspect-based summary chain,
    correcting the output using a JSON corrector chain if necessary.

    Args:
        doc (Document): The document to be summarized.
        index (int): The index of the document in the list, used for reference.
        question (str): The question to guide the summarization process.
        aspect_based_summary_chain (LLMChain): The LLMChain used for generating the summary.
        json_corrector_chain (LLMChain): The LLMChain used for correcting the JSON output if necessary.

    Returns:
        Tuple[int, Document]: A tuple containing the index of the document and the updated document with added metadata
        for summary and summary reasoning.

    Raises:
        Exception: Catches and logs exceptions related to JSON parsing and corrections, defaults summary details in
        the document's metadata.
    """
    use_full_documents = Container.config.get("use_full_documents", False)
    summary = "The text could not be summarized"
    summary_reasoning = "The text could not be summarized"

    if not use_full_documents:
        try:
            output_raw = aspect_based_summary_chain.run(retrieved_doc=doc.page_content, question=question)
            try:
                output_raw = output_raw.replace("```json", "").replace("```", "")
                output = json5.loads(output_raw)
            except Exception:  # pylint: disable=W0718
                json_output = json_corrector_chain.run(json=output_raw)
                json_output = json_output.replace("```json", "").replace("```", "")
                output = json5.loads(json_output)
            summary = output["summary"]
            summary_reasoning = output["summary_reasoning"]

        except Exception as e:  # pylint: disable=W0718
            print("Error in summarizing the document")
            print(str(e))
            summary = "The text could not be summarized"
            summary_reasoning = "The text could not be summarized"

    doc.metadata["summary"] = summary
    doc.metadata["summary_reasoning"] = summary_reasoning

    return index, doc


@trace_on("Only summarizing documents", measure_time=True)
def summarize_retrieved_documents(docs: List[Document], question: str) -> List[Document]:
    """
    Summarizes a list of documents with respect to a specific question using an aspect-based summary chain,
    performed in parallel to optimize processing time.

    This function takes a list of documents and a question, then uses a language model chain to generate
    summaries tailored to the question's context. Each document is processed in parallel using a ThreadPoolExecutor,
    which significantly speeds up the summarization process for large document sets. The summaries are integrated
    into the documents' metadata.

    Args:
        docs (List[Document]): A list of documents to be summarized. Each document should be an instance of the
            Document class with sufficient content for summarization.
        question (str): The question that guides the focus of the document summaries to ensure they are relevant
            to the query's context.

    Returns:
        List[Document]: The list of documents with updated metadata to include the summaries and any related reasoning
            or analysis derived from the summarization process.

    Raises:
        Exception: Handles exceptions related to failures in the summarization process, such as errors in parsing
            or correcting JSON output, and ensures that each document still returns with basic metadata adjustments.

    Note:
        This function initializes and uses an aspect-based summary chain and a JSON corrector chain from a dependency
        injection container. It is important that these components are properly configured before invocation.
    """
    aspect_based_summary_chain = Container.aspect_based_summary_chain()
    json_corrector_chain = Container.json_corrector_chain()
    summarized_docs = [" "] * len(docs)

    with ThreadPoolExecutor() as executor:
        future_to_doc = {
            executor.submit(summarize_document, doc, i, question, aspect_based_summary_chain, json_corrector_chain): doc
            for i, doc in enumerate(docs)
        }

        for future in as_completed(future_to_doc):
            index, doc = future.result()
            summarized_docs[index] = doc

    return summarized_docs


def score_previous_conversation(
    query_state: QueryState,
    index: int,
    question: str,
    previous_conversation_relevancy_chain: LLMChain,
    json_corrector_chain: LLMChain,
) -> Tuple[int, QueryState, int]:
    try:
        output_raw = previous_conversation_relevancy_chain.run(
            previous_question=query_state.question,
            previous_answer=query_state.answer,
            previous_additional_information_to_retrieve=query_state.additional_information_to_retrieve,
            question=question,
        )
        try:
            output_raw = output_raw.replace("```json", "").replace("```", "")
            output = json5.loads(output_raw)
        except Exception:  # pylint: disable=W0718
            json_output = json_corrector_chain.run(json=output_raw)
            json_output = json_output.replace("```json", "").replace("```", "")
            output = json5.loads(json_output)
        relevancy_score = int(output["relevancy_score"])
    except Exception as e:  # pylint: disable=W0718
        print("Error in parsing the document for relevancy score")
        print(str(e))
        relevancy_score = 0

    return index, query_state, relevancy_score


def filter_non_relevant_previous_conversations(query_states: list[QueryState], question) -> list[QueryState]:
    previous_conversation_relevancy_chain = Container.previous_conversation_relevancy_chain()
    json_corrector_chain = Container.json_corrector_chain()
    scored_query_states = [" "] * len(query_states)
    scores = [0] * len(query_states)
    with ThreadPoolExecutor() as executor:
        future_to_doc = {
            executor.submit(
                score_previous_conversation,
                query_state,
                i,
                question,
                previous_conversation_relevancy_chain,
                json_corrector_chain,
            ): query_state
            for i, query_state in enumerate(query_states)
        }

        for future in as_completed(future_to_doc):
            index, doc, relevancy_score = future.result()
            scored_query_states[index] = doc
            scores[index] = relevancy_score

    filtered_previous_conversations = []
    for i in range(len(scored_query_states)):
        if scores[i] >= Container.config.get("previous_conversation_score_threshold", 1):
            filtered_previous_conversations.append(scored_query_states[i])

    return filtered_previous_conversations


def print_doc_summary_and_relevance(docs_and_scores: list[Document]):
    """
    Print detailed summaries, relevancy reasoning, and scores for a list of documents.

    This function outputs the summary and relevance details of each document in the provided list,
    including section names, file names, data sources, policy numbers, and other metadata.

    Args:
        docs_and_scores (List[Document]): A list of Document objects that contain metadata including summaries and
        relevancy scores.

    Returns:
        None: This function does not return any values; it solely outputs to the console.

    Note:
        This function is typically used for debugging and presentation purposes to review the processed outputs
        of document summarization and scoring.
    """
    print("***** inside summarize_and_score_documents *****")
    print("---- Retriever output ----")
    print(*[d.metadata["section_name"] for d in docs_and_scores], sep="\n")
    for d in docs_and_scores:
        print("---- Section name ----")
        print(d.metadata["section_name"])
        print("---- File name ----")
        print(d.metadata["original_filepath"])
        print("---- Data Source ----")
        print(d.metadata["data_source"])
        print("---- Policy Number ----")
        print(d.metadata["policy_number"])
        print("---- Summary ----")
        print(d.metadata["summary"])
        print("---- Summary reasoning ----")
        print(d.metadata["summary_reasoning"])
        print("---- Relevance reasoning ----")
        print(d.metadata["relevancy_reasoning"])
        print("---- Relevance score ----")
        print(d.metadata["relevancy_score"])
        print("=====")
        print("")
    return None


@trace_on("Summarizing documents and scoring them", measure_time=True)
def summarize_and_score_documents(
    docs_and_scores: List[Document], question: str, threshold: int | None = None
) -> List[Document]:
    """
    Processes a list of documents by summarizing and scoring them based on a specified question,
    then filters the documents by a relevancy score threshold.

    This function first summarizes each document in the input list to focus its content more directly
    on the given question using `summarize_retrieved_documents`. It then scores these summarized documents
    for their relevance to the question with `score_retrieved_documents`. Finally, it filters and returns
    only those documents whose relevancy scores meet or exceed a predefined threshold,
    indicated by `retriever_score_threshold`.

    Args:
        docs_and_scores (List[Document]): A list of Document objects. Each Document should include
            any initial content and may include initial metadata (such as a pre-existing score).
        question (str): The question that guides the summarization and scoring of the documents,
            ensuring the relevance of the document's content to the question.

    Returns:
        List[Document]: A list of Document objects that have been summarized, scored, and filtered based
        on the relevancy score threshold. Each document's metadata includes the relevancy score.

    Note:
        - The `summarize_retrieved_documents` function is responsible for generating summaries of the
          documents based on the question.
        - The `score_retrieved_documents` function assigns a relevancy score to each summarized document,
          evaluating how well the document's content addresses the question.
        - The `retriever_score_threshold` is a predefined constant that specifies the minimum score a document
          must have to be considered relevant.
        - It is assumed that each Document object has a `metadata` attribute where the relevancy score can be
          accessed using the key `'relevancy_score'`.
    """
    print("Docs used before summary/scoring: ", len(docs_and_scores))
    threshold = threshold or Container.config.get("retriever_score_threshold", 2)
    docs_and_scores = summarize_retrieved_documents(docs_and_scores, question)
    docs_and_scores = score_retrieved_documents(docs_and_scores, question)
    if Container.debug_info:
        print_doc_summary_and_relevance(docs_and_scores)
    if Container.config["use_relevancy_score"]:
        docs_and_scores = [x for x in docs_and_scores if x.metadata["relevancy_score"] >= threshold]
    if Container.debug_info:
        print("---- Filtered documents ----")
        print(*[d.metadata["section_name"] for d in docs_and_scores], sep="\n")
        print("--------------------")
    print("Docs used after summary/scoring: ", len(docs_and_scores))
    return docs_and_scores
