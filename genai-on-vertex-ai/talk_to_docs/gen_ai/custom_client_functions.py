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
"""Talk2X Custom functions for specific use cases.

This module provides specialized classes and functions tailored for specific use 
cases and include document retrieval, processing, and storage.
"""

import concurrent.futures
import copy
import os
from collections import defaultdict
from datetime import datetime

from dependency_injector.wiring import inject
from langchain.schema import Document
from langchain_community.vectorstores.chroma import Chroma

import gen_ai.common.common as common
from gen_ai.common.common import TokenCounter, split_large_document, update_used_docs
from gen_ai.common.document_retriever import SemanticDocumentRetriever
from gen_ai.common.ioc_container import Container
from gen_ai.common.measure_utils import trace_on
from gen_ai.common.storage import Storage
from gen_ai.deploy.model import QueryState


def generate_contexts_from_docs(docs_and_scores: list[Document], query_state: QueryState | None = None) -> list[str]:
    return default_generate_contexts_from_docs(docs_and_scores, query_state)


def build_doc_title(metadata: dict[str, str]) -> str:
    """Builds a document title using chosen behavior.

    This function takes a dictionary containing various metadata fields, and
    concatenates these values to form a document title string.

    Args:
        metadata (dict[str, str]): A dictionary with potential metadata fields.

    Returns:
        str: A concatenated string containing the document title information
        based on the provided metadata fields.
    """
    return default_build_doc_title(metadata)


def extract_doc_attributes(docs_and_scores: list[Document]) -> list[tuple[str]]:
    """Extracts metadata attributes from a list of Document objects using chosen behavior.

    Args:
        docs_and_scores: A list of Document objects.

    Returns:
        A list of tuples where each tuple contains attributes from a Document.
    """
    return default_extract_doc_attributes(docs_and_scores)


def fill_query_state_with_doc_attributes(query_state: QueryState, post_filtered_docs: list[Document]) -> QueryState:
    """
    Updates the provided query_state object with attributes extracted from documents using chosen behavior.

    Args:
        query_state: The QueryState object to be modified.
        post_filtered_docs: A list of Document objects containing metadata.

    Returns:
        The modified QueryState object, with custom_fields updated based on document metadata.
    """
    return default_fill_query_state_with_doc_attributes(query_state, post_filtered_docs)


def default_fill_query_state_with_doc_attributes(
    query_state: QueryState, post_filtered_docs: list[Document]
) -> QueryState:
    """
    Updates the provided query_state object with attributes extracted from documents after filtering.

    This function iterates through each document in the `post_filtered_docs` list.  For each key-value
    pair in a document's metadata, it adds the value to the corresponding list in the `custom_fields`
    field of the `query_state`. If the key doesn't exist yet, a new list is created.

    Args:
        query_state: The QueryState object to be modified.
        post_filtered_docs: A list of Document objects containing metadata.

    Returns:
        The modified QueryState object, with custom_fields updated based on document metadata.
    """
    for document in post_filtered_docs:
        for key, value in document.metadata.items():
            if key not in query_state.custom_fields:
                query_state.custom_fields[key] = []
            query_state.custom_fields[key].append(value)

    return query_state, post_filtered_docs


def custom_fill_query_state_with_doc_attributes(
    query_state: QueryState, post_filtered_docs: list[Document]
) -> QueryState:
    """
    Updates the provided query_state object with attributes extracted from documents after filtering.

    This function modifies the query_state object by setting various attributes based on the metadata of documents
    in the post_filtered_docs list. It processes documents to categorize them by their data source
    (B360, KM or MP from KC), and updates the query_state with URLs, and categorized attributes for each type.

    Args:
        query_state (QueryState): The query state object that needs to be updated with document attributes.
        post_filtered_docs (list[Document]): A list of Document objects that have been filtered and whose attributes
        are to be extracted.

    Returns:
        QueryState: The updated query state object with new attributes set based on the provided documents.

    Side effects:
        Modifies the query_state object by setting the following attributes:
        - urls: A set of unique URLs extracted from the document metadata.
        - attributes_to_b360: A list of dictionaries with attributes from B360 documents.
        - attributes_to_kc_km: A list of dictionaries with attributes from KC KM documents.
        - attributes_to_kc_mp: A list of dictionaries with attributes from KC MP documents.

    """
    section_names = set(
        item.lower().strip() for x in query_state.relevant_context for item in (x if isinstance(x, list) else [x])
    )
    post_filtered_docs = [x for x in post_filtered_docs if x.metadata["section_name"] in section_names]

    query_state.urls = list(set(document.metadata["url"] for document in post_filtered_docs))

    # B360 documents
    b360_docs = [x for x in post_filtered_docs if x.metadata["data_source"] == "b360"]
    attributes_to_b360 = [
        {"set_number": x.metadata["set_number"], "section_name": x.metadata["section_name"]} for x in b360_docs
    ]

    # KC documents, they can be of two types: from KM (dont have policy number) and from MP (have policy number)
    kc_docs = [x for x in post_filtered_docs if x.metadata["data_source"] == "kc"]
    # kc_km_docs = [x for x in kc_docs if not x.metadata["policy_number"]]
    # kc_mp_docs = [x for x in kc_docs if x.metadata["policy_number"]]
    kc_km_docs = kc_docs
    kc_mp_docs = []

    attributes_to_kc_km = [
        {
            "doc_type": "km",
            "doc_identifier": x.metadata["doc_identifier"],
            "url": x.metadata["url"],
            "section_name": x.metadata["section_name"],
        }
        for x in kc_km_docs
    ]
    attributes_to_kc_mp = [
        {
            "doc_type": "mp",
            "original_filepath": x.metadata["original_filepath"],
            "policy_number": x.metadata["policy_number"],
            "section_name": x.metadata["section_name"],
        }
        for x in kc_mp_docs
    ]
    query_state.custom_fields["attributes_to_b360"] = attributes_to_b360
    query_state.custom_fields["attributes_to_kc_km"] = attributes_to_kc_km
    query_state.custom_fields["attributes_to_kc_mp"] = attributes_to_kc_mp

    return query_state, post_filtered_docs


def default_extract_doc_attributes(docs_and_scores: list[Document]) -> list[tuple[str]]:
    """Extracts all metadata attributes from a list of Document objects.

    Args:
        docs_and_scores: A list of Document objects, typically returned from a search operation.

    Returns:
        A list of tuples where each tuple contains all metadata attributes from a Document, in an
        arbitrary order. The order of the attributes in each tuple may vary depending on the
        underlying dictionary implementation.
    """
    return [tuple([value for _, value in x.metadata.items()]) for x in docs_and_scores]


def custom_extract_doc_attributes(docs_and_scores: list[Document]) -> list[tuple[str]]:
    """Extracts specific metadata attributes from a list of Document objects.

    Args:
        docs_and_scores: A list of Document objects, typically returned from a search operation.

    Returns:
        A list of tuples where each tuple contains the following metadata attributes from a Document:
            - original_filepath: The original file path of the document.
            - doc_identifier: A unique identifier for the document.
            - section_name: The name of the section within the document.
    """
    return [
        (x.metadata["original_filepath"], x.metadata["doc_identifier"], x.metadata["section_name"])
        for x in docs_and_scores
    ]


class CustomStorage(Storage):
    """
    Provides a customized document storage strategy for Retailer-specific document processing.
    This class handles text files by extracting their content, augmenting each document with
    metadata from a corresponding JSON file named similarly to the text file but with a '_metadata.json' suffix.

    Designed to work within a fixed plan name 'se', this class assumes all documents belong to a single
    organizational unit, making it specialized for scenarios where document categorization by plan name
    is uniform and predefined.
    """

    def process_directory(self, content_dir: str, extract_data_fn: callable) -> dict[str, list[Document]]:
        """
        Go through files in content_dir and parse their content if the filename ends with ".txt".
        Generate a document object from each file and store it in a hashmap where the key is the
        plan name and the value is a list of document objects. Return the hashmap.
        """

        documents_hashmap = defaultdict(list)
        plan_name = "se"
        for filename in os.listdir(content_dir):
            if filename.endswith(".txt") and "_metadata.json" not in filename:
                file_path = os.path.join(content_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                document = extract_data_fn(content)
                filename_metadata = file_path.replace(".txt", "_metadata.json")
                metadata = common.read_json(filename_metadata)
                for k, v in metadata.items():
                    document.metadata[k] = v

                documents_hashmap[plan_name].append(document)
        return documents_hashmap


class CustomSemanticDocumentRetriever(SemanticDocumentRetriever):
    """Implements document retrieval based on semantic similarity from a Chroma store.

    This retriever utilizes semantic similarity searches and max marginal relevance (MMR)
    algorithms to identify and rank documents from a Chroma vector store that are most
    relevant to a given query string. The process can be optionally refined using
    metadata filters to narrow down the search results further.

    Attributes:
        store (Chroma): The Chroma vector store instance from which documents are retrieved.
        questions_for_search (str): The query string used for finding related documents.
        metadata (dict, optional): Additional metadata for filtering the documents in the
            search query.
    """

    @trace_on("Retrieving documents from semantic store", measure_time=True)
    def get_related_docs_from_store(
        self, store: Chroma, questions_for_search: str, metadata: dict[str, str] | None = None
    ) -> list[Document]:
        # Very custom method
        if metadata is None or "policy_number" not in metadata:
            custom_metadata = {"data_source": "kc", "policy_number": "generic"}
            return self._get_related_docs_from_store(store, questions_for_search, custom_metadata)

        metadatas = []
        if "set_number" in metadata:
            b360_metadata = copy.deepcopy(metadata)
            b360_metadata["data_source"] = "b360"
            if "asof_date" in b360_metadata:
                asof_date = datetime.strptime(b360_metadata["asof_date"], "%Y-%m-%d")
                try:
                    end_date = asof_date.replace(year=asof_date.year - 1)
                except ValueError:
                    end_date = asof_date.replace(year=asof_date.year - 1, day=asof_date.day - 1)
                b360_metadata["effective_date <="] = asof_date
                b360_metadata["effective_date >"] = end_date
                del b360_metadata["asof_date"]
            metadatas.append(b360_metadata)

        kc_metadata = copy.deepcopy(metadata)
        kc_metadata["data_source"] = "kc"
        if "set_number" in kc_metadata:
            del kc_metadata["set_number"]
        if "asof_date" in kc_metadata:
            del kc_metadata["asof_date"]
        metadatas.append(kc_metadata)

        docs = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda m: self._get_related_docs_from_store(store, questions_for_search, m), metadatas
            )

        docs = []
        for result in results:
            docs.extend(result)

        return docs


def default_build_doc_title(metadata: dict[str, str]) -> str:
    """Constructs a document title string based on provided metadata.

    This function takes a dictionary containing various metadata fields,
    including "set_number," "section_name," "doc_identifier," and "policy_number."
    It concatenates these values to form a document title string.

    Args:
        metadata (dict[str, str]): A dictionary with potential metadata fields.
            - "set_number": An identifier representing the set number.
            - "section_name": The name of the relevant section.
            - "doc_identifier": A unique identifier for the document.
            - "policy_number": The specific number of the associated policy.
            - "symbols": The symbols of the document.

    Returns:
        str: A concatenated string containing the document title information
        based on the provided metadata fields.

    """
    doc_title = ""
    if metadata.get("set_number"):
        doc_title += metadata["set_number"] + " "
    if metadata.get("section_name"):
        doc_title += metadata["section_name"] + " "
    if metadata.get("doc_identifier"):
        doc_title += metadata["doc_identifier"] + " "
    if metadata.get("policy_number"):
        doc_title += metadata["policy_number"] + " "
    if metadata.get("symbols"):
        doc_title += metadata["symbols"] + " "
    # add excplicit section name
    if metadata.get("section_name"):
        doc_title += "\n" + "DOCUMENT SECTION NAME: " + metadata["section_name"] + " \n"
    return doc_title


def custom_generate_contexts_from_docs(
    docs_and_scores: list[Document], query_state: QueryState | None = None
) -> list[str]:
    kc_docs = [x for x in docs_and_scores if x.metadata["data_source"] == "kc"]
    b360_docs = [x for x in docs_and_scores if x.metadata["data_source"] == "b360"]
    kc_context = default_generate_contexts_from_docs(kc_docs, query_state)[0]
    b360_context = default_generate_contexts_from_docs(b360_docs, query_state)[0]

    custom_context = f"""
    <b360_context>
        {b360_context}
    </b360_context>
    This marks the start of text from kc documents. Remember that these are generic documents that will be overridden by a b360 documents, in case of a conflict re: coverage of a service.
    <kc_context>
        {kc_context}
    </kc_context>
    """
    return [custom_context]


@inject
@trace_on("Generating context from documents", measure_time=True)
def default_generate_contexts_from_docs(
    docs_and_scores: list[Document], query_state: QueryState | None = None
) -> list[str]:
    """
    Generates textual contexts from a list of documents, preparing them for input to a language model.

    This function processes each document to extract content up to a specified token limit, organizing this content
    into manageable sections that fit within the maximum context size for a language model. It handles large documents
    by splitting them into chunks and maintains a count of used tokens and documents to optimize the subsequent
    language model processing.

    Args:
        docs_and_scores (list[Document]): A list of Document objects, each containing metadata and content
            to be used in generating context. These documents are assumed to be scored and potentially filtered
            by relevance to the query.
        query_state (QueryState): The current state of the query, including details like previously used tokens
            and documents. This state is updated during the function execution to include details about the
            documents and tokens used in this invocation.

    Returns:
        list[str]: A list of strings, where each string represents a textual context segment formed from the
            document content. Each segment is designed to be within the token limits suitable for processing
            by a language model.

    Raises:
        ValueError: If any document does not contain the necessary content or metadata for processing.

    Examples:
        >>> docs = [Document(page_content="Content of the document.",
        metadata={"section_name": "Section 1", "summary": "Summary of the document.", "relevancy_score": 0.95})]
        >>> query_state = QueryState(question="What is the purpose of the document?",
        answer="To provide information.", additional_information_to_retrieve="")
        >>> contexts = generate_contexts_from_docs(docs, query_state)
        >>> print(contexts[0])
        "Content of the document."

    Note:
        The function modifies the `query_state` object in-place, updating it with details about the tokens and
        documents used during the context generation process. Ensure that the `query_state` object is appropriately
        handled to preserve the integrity of the conversation state.
    """
    num_docs_used = [0]
    contexts = ["\n"]
    token_counts = [0]
    used_articles = []
    token_counter: TokenCounter = Container.token_counter()
    max_context_size = Container.config.get("max_context_size", 1000000)

    for doc in docs_and_scores:
        filename = doc.metadata["section_name"]

        doc_content = doc.page_content if Container.config.get("use_full_documents", False) else doc.metadata["summary"]
        doc_tokens = token_counter.get_num_tokens_from_string(doc_content)
        if doc_tokens > max_context_size:
            doc_chunks = split_large_document(doc_content, max_context_size)
        else:
            doc_chunks = [(doc_content, doc_tokens)]

        for doc_chunk, doc_tokens in doc_chunks:

            if token_counts[-1] + doc_tokens >= max_context_size:
                token_counts.append(0)
                contexts.append("\n")
                num_docs_used.append(0)

            used_articles.append((f"{filename} Context: {len(contexts)}", doc.metadata["relevancy_score"]))
            token_counts[-1] += doc_tokens

            contexts[-1] += "DOCUMENT TITLE: "
            contexts[-1] += build_doc_title(doc.metadata) + "\n"
            contexts[-1] += "DOCUMENT CONTENT: "
            contexts[-1] += doc_chunk
            contexts[-1] += "\n" + "-" * 12 + "\n"
            num_docs_used[-1] += 1

    contexts[-1] += "\n"

    Container.logger().info(msg=f"Docs used: {num_docs_used}, tokens used: {token_counts}")

    if query_state:
        query_state.input_tokens = token_counts
        query_state.num_docs_used = num_docs_used
        query_state.used_articles_with_scores = update_used_docs(used_articles, query_state)
        Container.logger().info(msg=f"Doc names with relevancy scores: {query_state.used_articles_with_scores}")

    doc_attributes = extract_doc_attributes(docs_and_scores)
    Container.logger().info(msg=f"Doc attributes: {doc_attributes}")
    return contexts
