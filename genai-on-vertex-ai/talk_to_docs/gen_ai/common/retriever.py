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
This module facilitates the retrieval and processing of documents based on specific queries
using a combination of vector indices and language model chains. It primarily focuses on document
retrieval using different strategies and subsequent summarization and scoring of the retrieved
documents to assess their relevance to the given questions.

The module contains functions to execute retrieval rounds and initiate document retrieval with
the potential for personalized searches based on member-specific metadata. The retrieved documents
are then further processed to evaluate their relevance through summarization and scoring mechanisms
provided by integrated language model chains.

Functions:
    perform_retrieve_round(round_number, questions, vector_indices, document_retriever_name, member_info):
        Executes a document retrieval round using specified parameters and returns relevant documents.
    retrieve_initial_documents(round_number, question, vector_indices, document_retriever_name, member_info):
        Retrieves initial documents based on a query and processes them to enhance relevance and clarity.

Dependencies:
    langchain - Used for language model chain operations and document handling.
    gen_ai - Provides utilities for document retrieval and integration with AI models.
"""

from langchain.chains import LLMChain
from langchain.schema import Document
from langchain_community.vectorstores.chroma import Chroma

from gen_ai.common.providers import DocumentRetrieverProvider
from gen_ai.common.ioc_container import Container
from gen_ai.common.react_utils import summarize_and_score_documents


def perform_retrieve_round(
    round_number: int,
    questions: list[str],
    vector_indices: dict,
    document_retriever_name: str,
    member_info: dict | None = None,
) -> tuple[list[Document], list[Document]]:
    """
    Executes a retrieval round for a given question, using specified document retriever and vector indices.

    This method initiates a retrieval process for documents related to a specified question. It utilizes a
    document retriever identified by `document_retriever_name` to search for relevant documents within a
    store, potentially leveraging provided `vector_indices`. If `member_info` is provided, it customizes
    the retrieval process for each member in the list, allowing for personalized document retrieval based
    on member-specific metadata.

    Parameters
    ----------
    round_number : int
        The current round number of the retrieval process.
    question : str
        The question based on which documents are to be retrieved.
    vector_indices : dict
        A dictionary of vector indices used by the document retriever to find relevant documents.
    document_retriever_name : str
        The name of the document retriever to use for retrieving documents.
    member_info : dict | None, optional
        A dictionary, which contains metadata about a member for whom documents
        are being retrieved. This allows for personalized document retrieval. If `None`, the retrieval is
        not personalized.

    Returns
    -------
    list
        A list of dictionaries, where each dictionary contains information about a retrieved document
        and its relevance score with respect to the question. The list is sorted based on relevance scores.
    list
        A list of dictionaries, where each dictionary contains information about a post-filtered document
        and its relevance score with respect to the question. The list is sorted based on relevance scores.


    Raises
    ------
    Exception
        If there is an issue initializing the document retriever or retrieving documents.

    Examples
    --------
    >>> perform_retrieve_round(
    ...     round_number=1,
    ...     question="What is the capital of France?",
    ...     vector_indices={"index_name": "geo_index"},
    ...     document_retriever_name="basic_retriever"
    ... )
    [{'doc_id': '123', 'score': 0.95, 'text': 'The capital of France is Paris.'}, ...]

    Note: The actual implementation of `DocumentRetrieverProvider` and the method
    `get_related_docs_from_store` are assumed to be provided elsewhere in the application.
    """
    Container.logger().info(msg=f"Launching the retrieve round: {round_number}")
    document_provider = DocumentRetrieverProvider()
    document_retriever = document_provider(document_retriever_name)
    retrieved_docs = []
    if member_info is not None:
        docs = document_retriever.get_multiple_related_docs_from_store(vector_indices, questions, metadata=member_info)
        retrieved_docs = docs
    else:
        retrieved_docs = document_retriever.get_multiple_related_docs_from_store(vector_indices, questions)

    post_filtered_docs = summarize_and_score_documents(retrieved_docs, questions)
    return retrieved_docs, post_filtered_docs


def retrieve_initial_documents(
    round_number: int, question: str, vector_indices: Chroma, document_retriever_name: str, member_info: dict
) -> tuple[list[Document], list[Document]]:
    """
    Retrieves and processes initial documents for a given question by expanding the query to include similar questions
    and performing a retrieval round.

    This function enhances the initial query by generating similar questions using a language model, then uses these
    questions to retrieve and post-process documents. The documents are initially retrieved based on vector indices
    and further refined through summarization and scoring to evaluate their relevance.

    Args:
        round_number (int): The current round number of the retrieval process, used for tracking and logging.
        question (str): The initial question string based on which documents are retrieved.
        vector_indices (Chroma): The Chroma vector store used to locate relevant documents.
        document_retriever_name (str): The identifier for the document retriever to use.
        member_info (dict): Metadata about a member, used to personalize the document retrieval process.

    Returns:
        tuple[list[Document], list[Document]]: A tuple containing two lists:
            - The first list contains retrieved documents before post-processing.
            - The second list contains documents after being scored and summarized.

    Note:
        The function assumes that the similar questions chain is properly initialized in the Container and can generate
        relevant queries based on the initial question. Error handling for language model operations and vector store
        interactions is encapsulated within the retrieval functions.
    """

    if "?" not in question:
        question = f"{question}?"

    similar_questions = ""
    similar_questions_number = Container.config["similar_questions_number"]

    if similar_questions_number:
        similar_questions_chain: LLMChain = Container.similar_questions_chain()
        similar_questions = similar_questions_chain.run(
            question=question, similar_questions_number=similar_questions_number
        )
        Container.logger().info(msg=f"Questions:\n {similar_questions}")
        questions_for_search = question + "\n" + similar_questions
        questions_for_search = questions_for_search.split("?")
        questions_for_search = [x.replace("\n", "").strip() for x in questions_for_search]
        questions_for_search = [f"{x}?" for x in questions_for_search if x][0 : similar_questions_number + 1]
    else:
        questions_for_search = [question]

    Container.logger().info(msg=f"Questions after processing:\n {questions_for_search}")

    retrieved_docs, post_filtered_docs = perform_retrieve_round(
        round_number, questions_for_search, vector_indices, document_retriever_name, member_info
    )
    return retrieved_docs, post_filtered_docs
