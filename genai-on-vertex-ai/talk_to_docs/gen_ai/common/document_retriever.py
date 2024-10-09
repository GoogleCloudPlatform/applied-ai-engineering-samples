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
"""Provides classes for retrieving documents based on semantic analysis.

This module contains the `DocumentRetrieverProvider` for selecting the appropriate document
retriever based on a given criterion (e.g., semantic analysis) and the abstract base class
`DocumentRetriever` alongside its implementation, `SemanticDocumentRetriever`.

The `SemanticDocumentRetriever` is designed to retrieve related documents from a `Chroma`
vector store based on semantic similarity to a provided query, potentially filtered by
additional metadata criteria. It leverages similarity search and max marginal relevance
techniques to find and rank documents according to their relevance.
"""

import copy
from abc import ABC, abstractmethod
from typing import Any

from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents.base import Document

import gen_ai.common.common as common
from gen_ai.common.chroma_utils import convert_to_chroma_format, convert_to_vais_format
from gen_ai.common.ioc_container import Container
from gen_ai.common.measure_utils import trace_on


def remove_member_and_session_id(metadata: dict[str, Any]) -> dict[str, Any]:
    """Removes the "member_id" key and "session_id" from a metadata dictionary.

    This function creates a copy of the input dictionary, deletes the "member_id" and "session_id" key from
    the copy, and returns the modified copy.

    Args:
        metadata (dict): The input metadata dictionary.

    Returns:
        dict: A new dictionary with the "member_id" and "session_id" key removed.
    """
    new_metadata = copy.deepcopy(metadata)
    if "member_id" in new_metadata:
        del new_metadata["member_id"]
    if "session_id" in new_metadata:
        del new_metadata["session_id"]
    if "cob_status" in new_metadata:
        del new_metadata["cob_status"]
    return new_metadata


class DocumentRetriever(ABC):
    """
    Abstract base class for retrieving documents from a document store based on certain criteria.

    This class provides the framework for implementations that retrieve documents related to given queries.
    Subclasses must implement the `get_related_docs_from_store` method, which fetches documents based on
    semantic criteria or other specific conditions from a document store.

    Methods:
        get_related_docs_from_store(store, questions_for_search, metadata=None): Abstract method that must be
            implemented by subclasses to retrieve related documents based on the query and optional metadata.

        get_multiple_related_docs_from_store(store, questions_for_search, metadata=None): Retrieves multiple sets of
            documents for each question in a list. It aggregates results across multiple queries, removing duplicates
            and combining results from the individual document retrieval calls.

    Usage:
        Subclasses should provide specific implementations for fetching documents based on the criteria defined
        in `get_related_docs_from_store`. The `get_multiple_related_docs_from_store` method can be used directly
        by instances of the subclasses to handle multiple queries.
    """

    @abstractmethod
    def get_related_docs_from_store(
        self, store: Chroma, questions_for_search: str, metadata: dict = None
    ) -> list[Document]:
        pass

    def get_multiple_related_docs_from_store(
        self, store: Chroma, questions_for_search: list[str], metadata: dict[str, str] | None = None
    ):
        documents = []
        for question in questions_for_search:
            documents.extend(self.get_related_docs_from_store(store, question, metadata))
        documents = common.remove_duplicates(documents)
        return documents


class SemanticDocumentRetriever(DocumentRetriever):
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

    def _get_related_docs_from_store(
        self, store: Chroma, questions_for_search: str, metadata: dict[str, str] | None = None
    ) -> list[Document]:
        if metadata is None:
            metadata = {}
        metadata = remove_member_and_session_id(metadata)
        if Container.config.get("vector_name") == "chroma":
            if metadata is not None and len(metadata) > 1:
                metadata = convert_to_chroma_format(metadata)
        elif Container.config.get("vector_name") == "vais":
            metadata = convert_to_vais_format(metadata)

        ss_docs = store.similarity_search_with_score(query=questions_for_search, k=50, filter=metadata)
        max_number_of_docs_retrieved = Container.config.get("max_number_of_docs_retrieved", 3)
        ss_docs = [x[0] for x in ss_docs[0:max_number_of_docs_retrieved]]

        if Container.config.get("use_mmr", False):
            mmr_docs = store.max_marginal_relevance_search(
                query=questions_for_search, k=50, lambda_mult=0.5, filter=metadata
            )
            max_number_of_docs_retrieved_mmr = Container.config.get("max_number_of_docs_retrieved_mmr", 3)
            mmr_docs = mmr_docs[0:max_number_of_docs_retrieved_mmr]
        else:
            mmr_docs = []
        docs = common.remove_duplicates(ss_docs + mmr_docs)

        return docs

    @trace_on("Retrieving documents from semantic store", measure_time=True)
    def get_related_docs_from_store(
        self, store: Chroma, questions_for_search: str, metadata: dict[str, str] | None = None
    ) -> list[Document]:
        return self._get_related_docs_from_store(store, questions_for_search, metadata)

