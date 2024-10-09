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
"""Module for managing vectorization, vector storage, and retrieval strategies.

This module provides classes and functions for:

* **VectorStore:** Abstract base class defining vector search interfaces.
* **ChromaVectorStore:** Concrete implementation using Chroma for vector storage and search.
* **VertexVectorStore:**  Concrete implementation leveraging Vertex AI for vector storage and search.
* **VectorStrategy:** Abstract base class for vector embedding and index creation logic.
* **VectorStrategyProvider:** Provides a factory for selecting appropriate VectorStrategy.
* **ChromaVectorStrategy:**  Concrete implementation of VectorStrategy for Chroma.
* **VertexAIVectorStrategy:** Concrete implementation of VectorStrategy for Vertex AI.
"""

import glob
import json
import os
import random
import shutil
import string
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import google.auth
import pandas as pd
import requests
import tqdm
from google.api_core.client_options import ClientOptions
from google.cloud import aiplatform
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.cloud import storage
from langchain.schema import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores import Chroma

from gen_ai.common.chroma_utils import map_composite_to_dict
from gen_ai.common.common import default_extract_data
from gen_ai.common.exponential_retry import retry_with_exponential_backoff
from gen_ai.common.inverted_index import InvertedIndex
from gen_ai.common.storage import Storage


@dataclass
class DeployedEndpoint:
    """Class for keeping track of Deployed Endpoints."""

    index: str
    index_endpoint_name: str
    deployed_index_endpoint_name: str
    plan: str


class VectorStore(ABC):
    """Abstract base class for vector stores.

    Defines the interface for similarity search and maximum marginal relevance search.
    """

    @abstractmethod
    def similarity_search(self, query: str, k: int = 4, **kwargs) -> list[Document]:
        """Performs a similarity search on the vector store.

        Args:
            query: The query text.
            k: The number of results to return. Defaults to 4.
            **kwargs: Additional arguments to be passed to the underlying implementation.

        Returns:
            A list of LangChain Document objects representing the results.
        """
        pass

    @abstractmethod
    def max_marginal_relevance_search(
        self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs
    ) -> list[Document]:
        """Performs a maximum marginal relevance (MMR) search on the vector store.

        Args:
            query: The query text.
            k: The number of results to return. Defaults to 4.
            fetch_k:  The number of documents to initially retrieve. Defaults to 20
            lambda_mult: Multiplier for controlling MMR tradeoff. Defaults to 0.5.
            **kwargs: Additional arguments to be passed to the underlying implementation.

        Returns:
            A list of LangChain Document objects representing the results.
        """
        pass


class VectorStrategy(ABC):
    """Abstract base class for defining vector embedding and index creation strategies.

    This class provides a blueprint for managing the process of generating vector
    embeddings for documents and creating vector indices for efficient similarity
    search. Concrete subclasses are responsible for implementing the specific logic
    for different vector storage and retrieval systems (e.g., Chroma, Vertex AI).

    Attributes:
        storage_interface: An interface for interacting with storage systems
            to retrieve documents for indexing.
        config: A dictionary containing configuration parameters for the
            vector strategy.
    """

    def __init__(self, storage_interface: Storage, config: dict[str, str]):
        """Initializes VectorStrategy with storage interface and configuration.

        Args:
            storage_interface: An instance of a class implementing the Storage
                interface, providing methods to access and retrieve documents.
            config: A dictionary holding configuration settings for the vector strategy.
                The specific keys and values depend on the concrete subclass implementation.
        """
        self.storage_interface = storage_interface
        self.config = config

    @abstractmethod
    def get_vector_indices(
        self, regenerate: bool, embeddings: Embeddings, vector_indices: dict[str, str], processed_files_dir: str
    ) -> dict[str, str]:
        """Retrieves or creates vector indices based on the provided configuration.

        This method is responsible for either retrieving existing vector indices
        or creating new ones based on the provided configuration and data.

        Args:
            regenerate: If True, forces the regeneration of vector indices,
                even if they already exist. If False, existing indices will be loaded
                if available.
            embeddings: An instance of an embedding model that will be used to
                generate vector representations of documents during index creation.
            vector_indices: A dictionary representing existing vector indices,
                where keys are plan names and values are the corresponding index objects.
                This parameter can be an empty dictionary if no indices exist.
            processed_files_dir: The directory path where processed files
                (e.g., text documents) are stored. These files will be used
                as input for generating vector embeddings and creating the index.

        Returns:
            A dictionary mapping plan names to their corresponding vector indices.
            The structure of the index objects depends on the specific vector store
            implementation (e.g., Chroma, Vertex AI).
        """
        raise NotImplementedError("Cannot be invoked directly from abstract class")


class ChromaVectorStore(VectorStore):
    """Concrete implementation of VectorStore using Chroma for vector storage and search.

    Attributes:
        chroma: The Chroma instance for managing the vector store.
    """

    def __init__(self, chroma: Chroma):
        """Initializes ChromaVectorStore with a Chroma instance.
        Args:
            chroma: An instance of a ChromaDB class from Langchain.
        """
        self.chroma = chroma

    def similarity_search(self, query: str, k: int = 4, **kwargs) -> list[Document]:
        """Performs a similarity search using the Chroma vector store.

        Args:
            query: The query text.
            k: The number of results to return. Defaults to 4.
            **kwargs: Additional arguments passed to Chroma's similarity_search.

        Returns:
            A list of LangChain Document objects representing the results.
        """
        return self.chroma.similarity_search(query, k, **kwargs)

    def max_marginal_relevance_search(
        self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs
    ) -> list[Document]:
        """Performs MMR search using the Chroma vector store.

        Args:
            query: The query text.
            k: The number of results to return. Defaults to 4.
            fetch_k: The number of documents to initially retrieve. Defaults to 20.
            lambda_mult: Multiplier for controlling MMR tradeoff. Defaults to 0.5.
            **kwargs: Additional arguments passed to Chroma's MMR search.

        Returns:
            A list of LangChain Document objects representing the results.
        """
        return self.chroma.max_marginal_relevance_search(query, k, fetch_k, lambda_mult, **kwargs)


class VertexVectorStore(VectorStore):
    """Concrete implementation of VectorStore using Vertex AI for vector storage and search.

    Attributes:
        vertex: Vertex AI endpoint instance.
        index_id: The ID of the Vertex AI index.
        embeddings: The embedding model used for generating vectors.
        doc_mapping:  Mapping between document IDs and their textual content/metadata.
    """

    def __init__(
        self, vertex: aiplatform.MatchingEngineIndexEndpoint, index_id: str, embeddings: Embeddings, doc_mapping: dict
    ):
        """Initializes VertexVectorStore with endpoint, index ID, embeddings, and document mapping.

        Args:
            vertex: Vertex AI endpoint instance.
            index_id: The ID of the Vertex AI index.
            embeddings: The embedding model used for generating vectors.
            doc_mapping: Mapping between document IDs and their textual content/metadata.
        """
        self.vertex = vertex
        self.index_id = index_id
        self.embeddings = embeddings
        self.doc_mapping = doc_mapping

    def convert_to_langchain(self, neighbours: list) -> list[Document]:
        """Converts Vertex AI search results to LangChain Documents.

        Args:
            neighbours: List of neighbors returned from Vertex AI search.

        Returns:
            List of LangChain Document objects.
        """
        docs = []
        for match in neighbours[0]:
            if match.id in self.doc_mapping:
                text = self.doc_mapping[match.id][0]
                metadata = self.doc_mapping[match.id][1]
                doc = Document(page_content=text, metadata=metadata)
                docs.append(doc)
        return docs

    def similarity_search(self, query: str, k: int = 4, **kwargs) -> list[Document]:
        """Performs a similarity search using the Vertex AI vector store.

        Args:
            query: The query text.
            k: The number of results to return. Defaults to 4.
            **kwargs: Not used, present for compatibility.

        Returns:
            A list of LangChain Document objects representing the results.
        """
        embs = self.embeddings.embed_documents([query])
        neighbours = self.vertex.find_neighbors(num_neighbors=k, queries=embs, deployed_index_id=self.index_id)
        docs = self.convert_to_langchain(neighbours)
        return docs

    def max_marginal_relevance_search(
        self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs
    ) -> list[Document]:
        """Not supported by Vertex AI, delegates to similarity_search.

        Args:
            query: The query text.
            k: The number of results to return. Defaults to 4.
            fetch_k: Not used, present for compatibility.
            lambda_mult: Not used, present for compatibility.
            **kwargs: Not used, present for compatibility.

        Returns:
            A list of LangChain Document objects representing the results.
        """
        # vertex AI does not support max marginal search, so we just use similarity search under the hood
        return self.similarity_search(query, k, **kwargs)


class VertexAISearchVectorStore(VectorStore):
    """VectorStore implementation utilizing Vertex AI Search for storage and retrieval.

    This class seamlessly integrates with Vertex AI Search (VAIS), Google's powerful
    search and recommendation platform, to store and retrieve documents based on
    semantic similarity.

    Key Features:

    * **Semantic Search:** Employs VAIS's advanced algorithms to understand the meaning of queries and documents,
    leading to more relevant results.
    * **Filtering:** Supports filtering documents during retrieval, allowing for targeted search results
    based on metadata.
    * **Query Expansion:** Leverages VAIS's query expansion capabilities to automatically broaden searches
    and improve recall.
    * **Spell Correction:** Automatically corrects spelling errors in queries to enhance search accuracy.

    Note: This class is distinct from `VertexVectorStore`.
          Ensure you are using the correct one based on your needs.

    Args:
        project_id: Your Google Cloud Project ID.
        engine_id: The ID of your Vertex AI Search engine.
        config: Configuration for the vector store.

    Attributes:
        project_id: The Google Cloud Project ID.
        location: The location of the Vertex AI Search engine.
        engine_id: The ID of the Vertex AI Search engine.
        config: Configuration for the vector store.
        use_prev_and_next_pieces: Whether to include previous and next pieces of text.
        location: The location of the Vertex AI Search resources.
        vais_data_store_mode: The mode of the Vertex AI Search data store.

    Methods:
        _search_sample: Internal method to perform a search using Vertex AI Search.
        similarity_search_with_score: Performs a semantic search with scores for relevance.
        similarity_search: Performs a semantic search without scores (delegates to `similarity_search_with_score`).
        max_marginal_relevance_search: Currently not implemented.
    """

    def __init__(self, project_id: str, engine_id: str, config: dict):
        """Initializes VertexAISearchVectorStore with project, engine, and data store IDs.

        Args:
            project_id: Your Google Cloud Project ID.
            engine_id: The ID of your Vertex AI Search engine.
            config: Configuration for the vector store.
        """
        self.project_id = project_id
        self.engine_id = engine_id
        self.config = config
        self.use_prev_and_next_pieces = self.config.get("use_prev_and_next_pieces", 0)
        self.location = self.config.get("vais_location", "global")
        self.vais_data_store_mode = self.config.get("vais_data_store_mode", "extractive")

    @retry_with_exponential_backoff()
    def perform_search_request(
        self, client: discoveryengine.SearchServiceClient, request: discoveryengine.SearchRequest
    ) -> discoveryengine.SearchResponse:
        """Performs a search request with retries.

        Args:
            client: Vertex AI Search client.
            request: The search request.

        Returns:
            The search response.
        """
        response = client.search(request)
        return response

    def _search_sample(
        self,
        project_id: str,
        location: str,
        engine_id: str,
        search_query: str,
        k: int = 4,
        filter: str = None,  # pylint: disable=redefined-builtin
        **kwargs,  # pylint: disable=unused-argument
    ) -> list[tuple[Document, float]]:
        """Internal method to perform a raw search using Vertex AI Search.

        This method interacts with the Vertex AI Search API to retrieve documents
        relevant to the given search query. It returns a list of tuples, each
        containing a Document object and its relevance score.

        Args:
            project_id: Your Google Cloud Project ID.
            location: The location of your Vertex AI Search engine.
            engine_id: The ID of your Vertex AI Search engine.
            search_query: The text query to search for.
            k: The number of results to return (defaults to 4).
            filter: A filter expression to narrow down results.

        Returns:
            A list of tuples where each tuple contains a Document
            and its corresponding relevance score.
        """
        docs = []

        client_options = (
            ClientOptions(api_endpoint=f"{self.location}-discoveryengine.googleapis.com")
            if self.location != "global"
            else None
        )
        client = discoveryengine.SearchServiceClient(client_options=client_options)
        serving_config = (
            f"projects/{project_id}/locations/{self.location}/"
            f"collections/default_collection/engines/{engine_id}/"
            "servingConfigs/default_config"
        )
        if self.vais_data_store_mode == "extractive":
            content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_segment_count=1,
                    return_extractive_segment_score=True,
                    num_previous_segments=self.use_prev_and_next_pieces,
                    num_next_segments=self.use_prev_and_next_pieces,
                ),
            )
        elif self.vais_data_store_mode == "chunk":
            content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
                chunk_spec=discoveryengine.SearchRequest.ContentSearchSpec.ChunkSpec(
                    num_previous_chunks=self.use_prev_and_next_pieces,
                    num_next_chunks=self.use_prev_and_next_pieces,
                ),
                search_result_mode="CHUNKS",
            )
        else:
            raise ValueError("Not correct mode for vais is passed, should be chunk/extractive")

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=min(10, k),
            content_search_spec=content_search_spec,
            filter=filter,  # pylint: disable=redefined-builtin
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
        )

        response = self.perform_search_request(client, request)
        ls = response.results
        if self.vais_data_store_mode == "extractive":
            docs = self.get_extractive_segments(ls)
        elif self.vais_data_store_mode == "chunk":
            docs = self.get_chunks(ls)
        else:
            raise ValueError("Not correct mode for vais is passed, should be chunk/extractive")
        return docs

    def get_chunks(self, ls: list[discoveryengine.SearchResponse]) -> list[tuple[Document, float]]:
        """Extracts document chunks from VAIS search results.

        Args:
            ls: List of VAIS SearchResult objects.

        Returns:
            List of tuples, each containing a Document and its score.
        """
        docs = []
        for item in ls:
            try:
                previous_content = (
                    self._build_next_and_previous_content(
                        item.chunk.chunk_metadata.previous_chunks, lambda x: x.content, True
                    )
                    if len(item.chunk.chunk_metadata.previous_chunks) >= 1
                    else ""
                )
                next_content = (
                    self._build_next_and_previous_content(item.chunk.chunk_metadata.next_chunks, lambda x: x.content)
                    if len(item.chunk.chunk_metadata.next_chunks) >= 1
                    else ""
                )
                central_content = item.chunk.content

                content = f"{previous_content}\n{central_content}\n{next_content}"
                metadata = map_composite_to_dict(item.chunk.document_metadata.struct_data)
                score = 0.9  # we use 0.9 as default value, because we don't sort on relevancy score
                doc = Document(page_content=content)
                doc.metadata = metadata
                docs.append((doc, score))
            except Exception as e:  # pylint: disable=broad-exception-caught
                print("Exception happened on parsing:", item)
                print(e)
                continue
        return docs

    def _build_next_and_previous_content(
        self, chunks: list[discoveryengine.SearchResponse], content_functor: callable, reverse: bool = False
    ) -> str:
        """Constructs the content from previous or next chunks.

        Args:
            chunks: List of chunks to extract content from.
            content_functor: Function to apply to each chunk to get its content.
            reverse: Whether to reverse the order of chunks.

        Returns:
            The combined content from the chunks.
        """
        content = []
        for i in range(len(chunks)):
            content.append(content_functor(chunks[i]))
            content.append("\n")

        if reverse:
            content = content[::-1]
        return "".join(content)

    def get_extractive_segments(self, ls: list[discoveryengine.SearchResponse]) -> list[tuple[Document, float]]:
        """Extracts extractive segments from VAIS search results.

        Args:
            ls: List of VAIS SearchResult objects.

        Returns:
            List of tuples, each containing a Document and its score.
        """
        docs = []
        for item in ls:
            try:
                extractive_segment = item.document.derived_struct_data["extractive_segments"][0]
                previous_content = (
                    self._build_next_and_previous_content(
                        extractive_segment["previous_segments"], lambda x: x["content"], True
                    )
                    if "previous_segments" in extractive_segment
                    else ""
                )
                next_content = (
                    self._build_next_and_previous_content(extractive_segment["next_segments"], lambda x: x["content"])
                    if "next_segments" in extractive_segment
                    else ""
                )
                central_content = item.document.derived_struct_data["extractive_segments"][0]["content"]
                content = f"{previous_content}\n{central_content}\n{next_content}"

                score = item.document.derived_struct_data["extractive_segments"][0]["relevanceScore"]
                doc = Document(page_content=content)
                struct_data_dict = map_composite_to_dict(item.document.struct_data)
                doc.metadata = struct_data_dict
                docs.append((doc, score))
            except Exception as e:  # pylint: disable=broad-exception-caught
                print("Exception happened on parsing:", item.document.struct_data["data_source"])
                print(e)
                continue

        return sorted(docs, key=lambda x: x[1], reverse=True)

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter: str = None, **kwargs  # pylint: disable=redefined-builtin
    ) -> list[tuple[Document, float]]:
        """Performs a semantic similarity search and returns results with scores.

        Args:
            query: The query text to search for.
            k: The number of top results to return (defaults to 4).
            filter: A filter expression to apply to the search.
            **kwargs: Additional keyword arguments (not used).

        Returns:
            A list of tuples where each tuple contains a Document
            and its relevance score (higher is more relevant).
        """
        return self._search_sample(
            project_id=self.project_id,
            location=self.location,
            engine_id=self.engine_id,
            search_query=query,
            k=k,
            filter=filter,
            **kwargs,
        )

    def similarity_search(
        self, query: str, k: int = 4, filter: str = None, **kwargs  # pylint: disable=redefined-builtin
    ) -> list[Document]:
        """Performs a semantic similarity search and returns documents only.

        This method is a convenience wrapper around `similarity_search_with_score` that
        discards the relevance scores.

        Args:
            query: The query text to search for.
            k: The number of top results to return (defaults to 4).
            filter: A filter expression to apply to the search.
            **kwargs: Additional keyword arguments (not used).

        Returns:
            A list of the most relevant documents to the query.
        """
        return [doc for doc, _ in self.similarity_search_with_score(query, k, filter)]

    def max_marginal_relevance_search(
        self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs
    ) -> list[Document]:
        """Not currently implemented."""
        return []


class VectorStrategyProvider:
    """Factory class for selecting the appropriate VectorStrategy implementation."""

    def __init__(self, vector_name):
        self.vector_name = vector_name

    def __call__(self, **kwargs) -> VectorStrategy:
        """Provides the vector strategy.
        Vector strategy consists of two functionalities: vector embeddings and vector indices creation

        Raises:
            ValueError: currently supports openai and vertexai strategies. Raises exception if other types are
            specified

        Returns:
            Embeddings: langchain class of base embeddings
        """
        print(f"Loading {self.vector_name} Vector Strategy...")
        if "vertexai" in self.vector_name:
            return VertexAIVectorStrategy(**kwargs)
        elif "vais" in self.vector_name:
            return VertexAISearchVectorStrategy(**kwargs)
        elif "chroma" in self.vector_name:
            return ChromaVectorStrategy(**kwargs)
        else:
            raise ValueError("Not supported embeddings name in config")


class ChromaVectorStrategy(VectorStrategy):
    """Concrete implementation of VectorStrategy for using Chroma as the vector store."""

    def __init__(self, storage_interface: Storage, config: dict[str, str], vectore_store_path: str) -> None:
        super().__init__(storage_interface, config)
        self.vectore_store_path = f"{vectore_store_path}_chroma"

    def get_vector_indices(
        self, regenerate: bool, embeddings: Embeddings, vector_indices: dict[str, str], processed_files_dir: str
    ):
        if not os.path.exists(self.vectore_store_path) or regenerate:
            if os.path.exists(self.vectore_store_path):
                try:
                    os.rmdir(self.vectore_store_path)
                except OSError as _:
                    os.removedirs(self.vectore_store_path)

            docs = self.storage_interface.process_directory(processed_files_dir, default_extract_data)
            plan_store = Chroma.from_documents(docs, embeddings, persist_directory=self.vectore_store_path)
            plan_store.persist()
            vector_indices = plan_store
        else:
            plan_store = Chroma(persist_directory=self.vectore_store_path, embedding_function=embeddings)
            vector_indices = plan_store

        return vector_indices


class VertexAISearchVectorStrategy(VectorStrategy):
    """Strategy to use Vertex AI Search (VAIS) as the vector store for document retrieval.

    This class handles the setup and interaction with Vertex AI Search to store
    document embeddings and perform semantic searches. It provides functionality to:

    * **Prepare data:** Convert documents into the format required by VAIS.
    * **Create resources:** Create data stores and search engines on VAIS.
    * **Manage VAIS configuration:** Serialize and deserialize VAIS engine IDs for persistence.
    * **Integrate with LlamaIndex:** Provide a `VertexAISearchVectorStore` instance for document retrieval.

    Args:
        storage_interface (Storage): The LlamaIndex storage interface for data persistence.
        config (dict[str, str]): Configuration dictionary containing:
            * "dataset_name": The name for the VAIS dataset.
            * "bq_project_id": The Google Cloud project ID for Vertex AI and BigQuery.
        vectore_store_path (str): The base directory to store VAIS configuration.

    Attributes:
        vectore_store_path (str): The directory to store VAIS configuration.
        config (dict[str, str]): The configuration dictionary.
    """

    def __init__(self, storage_interface: Storage, config: dict[str, str], vectore_store_path: str) -> None:
        """Initializes VertexAISearchVectorStrategy with storage, config, and store path.

        Args:
            storage_interface: The LlamaIndex storage interface for data persistence.
            config: Configuration dictionary containing VAIS settings.
            vectore_store_path: The base directory to store VAIS configuration.
        """
        super().__init__(storage_interface, config)
        self.vectore_store_path = f"{vectore_store_path}_vais"
        self.config = config
        self.location = self.config.get("vais_location", "global")
        if self.location == "global":
            self.base_url = "https://discoveryengine.googleapis.com/v1"
        else:
            self.base_url = f"https://{self.location}-discoveryengine.googleapis.com/v1"

    def get_vector_indices(
        self, regenerate: bool, embeddings: Embeddings, vector_indices: dict[str, str], processed_files_dir: str
    ):
        """Gets or creates a VertexAISearchVectorStore instance.

        If a VAIS engine exists in the `vectore_store_path`, it will be loaded.
        Otherwise, a new engine will be created using the provided configuration and data.

        Args:
            regenerate (bool): Unused argument (kept for compatibility with base class).
            embeddings (Embeddings): Unused argument (kept for compatibility with base class).
            vector_indices (dict[str, str]): Unused argument (kept for compatibility with base class).
            processed_files_dir (str): The directory containing processed files for VAIS.

        Returns:
            VertexAISearchVectorStore: A Vertex AI Search-backed vector store instance.
        """
        aiplatform.init()
        project_id = self.config.get("bq_project_id")
        if not project_id:
            _, project_id = google.auth.default()

        waize_data_store = self.config.get("vais_data_store")
        waize_engine_id = self.config.get("vais_engine_id")
        if waize_data_store and waize_engine_id:
            print("VAIS engine and data store values provided in llm.yaml")
            self.__serialize_engine_id(waize_engine_id, waize_data_store, "engine_and_store_already_exist")

        if not os.path.exists(self.vectore_store_path):
            print("No VAIS vector store found, creating one...")
            dataset_name = self.config.get("dataset_name")
            vais_staging_bucket = self.config.get("vais_staging_bucket", None)

            waize_gcs_uri = self.__prepare_waize_format(processed_files_dir, dataset_name, vais_staging_bucket)
            waize_data_store = self.__create_waize_data_store(project_id, dataset_name, self.location)
            waize_data_store = self.__import_data_to_waize_data_store(
                project_id, waize_data_store, waize_gcs_uri, self.location
            )
            waize_engine_id = self.__create_waize_app(project_id, dataset_name, waize_data_store, self.location)
            self.__serialize_engine_id(waize_engine_id, waize_data_store, waize_gcs_uri)
            print("VAIS vector store created successfully... waiting for Enterprise Features Activation")
            time.sleep(90)  # timeout for enterprise features to activate. Talk to Hossein about it
        else:
            print("VAIS vector store exists, retrieving the values...")
        waize_engine_id, waize_data_store = self.__deserialize_engine_id()

        return VertexAISearchVectorStore(project_id, waize_engine_id, self.config)

    def __deserialize_engine_id(self):
        """Deserializes the VAIS engine ID from a JSON file.

        Returns:
            str: The VAIS engine ID.
        """
        vais_path = os.path.join(self.vectore_store_path, "vais_urls.json")
        with open(vais_path, "r", encoding="utf-8") as f:
            vais_urls = json.load(f)
        print(f"VAIS urls are: \n {vais_urls}")
        return vais_urls["vais_engine_id"], vais_urls["vais_data_store"]

    def __serialize_engine_id(self, waize_engine_id, waize_data_store, waize_gcs_uri):
        """Serializes the VAIS engine ID and related URLs to a JSON file.

        Args:
            waize_engine_id (str): The VAIS engine ID.
            waize_data_store (str): The VAIS data store ID.
            waize_gcs_uri (str): The GCS URI of the JSONL data.
        """
        os.makedirs(self.vectore_store_path, exist_ok=True)
        vais_path = os.path.join(self.vectore_store_path, "vais_urls.json")
        vais_urls = {
            "vais_engine_id": waize_engine_id,
            "vais_data_store": waize_data_store,
            "vais_gcs_uri": waize_gcs_uri,
        }
        with open(vais_path, "w", encoding="utf-8") as f:
            json.dump(vais_urls, f)

        print(f"Saved VAIS urls to {vais_path}")
        print(f"VAIS urls are: \n {vais_urls}")

    def __prepare_waize_format(self, processed_dir, dataset_name, bucket_name=None):
        """Prepares data for VAIS import.

        Creates a JSONL file from processed files and uploads it to a new GCS bucket.
        If `bucket_name` is provided, files are read from that bucket instead of `processed_dir`.

        Args:
            processed_dir (str): The directory containing processed files (used if `bucket_name` is None).
            dataset_name (str): The name to use for the dataset.
            bucket_name (str, optional): The name of the GCS bucket to read files from.

        Returns:
            str: The name of the new GCS bucket.
        """
        print("Preparing format for VAIS...")
        storage_client = storage.Client()

        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        new_bucket_name = f"{dataset_name}-jsonl-{random_suffix}"
        new_bucket = storage_client.bucket(new_bucket_name)
        new_bucket.create()

        print(f"Copying the Documents and JSONL file to bucket: {new_bucket_name}")
        jsonl_data = []

        if bucket_name:
            source_bucket = storage_client.bucket(bucket_name)
            blobs = source_bucket.list_blobs()
            all_files = [blob.name for blob in blobs]
        else:
            all_files = list(os.listdir(processed_dir))

        for i, filename in tqdm.tqdm(enumerate(all_files), total=len(all_files)):
            if filename.endswith("_metadata.json"):
                file_name_base = filename[:-14]  # Remove "_metadata.json"
                txt_file_name = f"{file_name_base}.txt"

                if bucket_name:
                    # Download files from the source bucket
                    metadata_blob = source_bucket.blob(filename)
                    metadata_str = metadata_blob.download_as_string().decode("utf-8")
                    metadata = json.loads(metadata_str)

                    txt_blob = source_bucket.blob(f"data/{txt_file_name}")
                    new_blob_name = f"data/{txt_file_name}"
                    source_bucket.copy_blob(txt_blob, new_bucket, new_blob_name)
                else:
                    # Read files from the local directory
                    txt_file_path = os.path.join(processed_dir, txt_file_name)
                    if not os.path.isfile(txt_file_path):
                        continue  # Skip if no matching TXT file

                    metadata_path = os.path.join(processed_dir, filename)
                    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
                        metadata = json.load(metadata_file)
                    metadata_str = json.dumps(metadata)

                    txt_blob = new_bucket.blob(f"data/{txt_file_name}")
                    txt_blob.upload_from_filename(txt_file_path)

                jsonl_entry = {
                    "id": str(i),
                    "jsonData": metadata_str,
                    "content": {"mimeType": "text/plain", "uri": f"gs://{new_bucket_name}/data/{txt_file_name}"},
                }
                jsonl_data.append(jsonl_entry)

        jsonl_path = "output.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as outfile:
            for entry in jsonl_data:
                outfile.write(json.dumps(entry) + "\n")
        jsonl_blob = new_bucket.blob(jsonl_path)
        jsonl_blob.upload_from_filename(jsonl_path)
        if os.path.exists(jsonl_path):
            os.remove(jsonl_path)

        return new_bucket_name

    def __create_waize_data_store(self, project_id, dataset_name, location) -> str:
        """Creates a data store in Vertex AI Search.

        Args:
            project_id (str): The Google Cloud project ID.
            dataset_name (str): A name to incorporate into the data store ID.

        Returns:
            str: The ID of the created data store.
        """
        print("Creating the Data Store for VAIS...")
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        new_data_store = f"data_store-{dataset_name}-{random_suffix}"
        new_data_store_name = f"Data store: {new_data_store}"

        access_token = subprocess.check_output("gcloud auth print-access-token", shell=True, text=True).strip()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": project_id,
        }

        url = (
            f"{self.base_url}/projects/{project_id}/"
            f"locations/{location}/collections/default_collection/dataStores"
            f"?dataStoreId={new_data_store}"
        )
        if self.config.get("vais_data_store_mode", "extractive") == "extractive":
            data = {
                "displayName": f"{new_data_store_name}",
                "industryVertical": "GENERIC",
                "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
                "contentConfig": "CONTENT_REQUIRED",
            }
        else:
            data = {
                "displayName": f"{new_data_store_name}",
                "industryVertical": "GENERIC",
                "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
                "contentConfig": "CONTENT_REQUIRED",
                "documentProcessingConfig": {
                    "chunkingConfig": {
                        "layoutBasedChunkingConfig": {
                            "chunkSize": 500,
                            "includeAncestorHeadings": True,
                        }
                    },
                    "defaultParsingConfig": {"layoutParsingConfig": {}},
                },
            }

        response = requests.post(url, headers=headers, json=data, timeout=3600)

        response.raise_for_status()

        return new_data_store

    def __import_finished(self, project_id: str, data_store_id: str, location):
        """Checks if the import to the Vertex AI Search data store is finished.

        Args:
            project_id (str): The Google Cloud project ID.
            data_store_id (str): The ID of the data store.

        Returns:
            bool: True if import is finished, False otherwise.
        """
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") if location != "global" else None
        )

        client = discoveryengine.DocumentServiceClient(client_options=client_options)
        parent = client.branch_path(
            project=project_id,
            data_store=data_store_id,
            location=location,
            branch="default_branch",
        )
        print("Checking status of import to VAIS")
        try:
            response = client.list_documents(parent=parent)
            if len(list(response)) > 0:
                return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error: {e}")
            return False

    def __import_data_to_waize_data_store(self, project_id, data_store_id, waize_gcs_uri, location):
        """Imports data to the Vertex AI Search data store from GCS.

        Args:
            project_id (str): The Google Cloud project ID.
            data_store_id (str): The ID of the data store.
            waize_gcs_uri (str): The GCS URI of the JSONL data to import.

        Returns:
            str: The ID of the data store.
        """
        print(f"Importing the Documents to Data Store: {data_store_id}...")
        url = (
            f"{self.base_url}/projects/{project_id}/locations/{location}/collections/default_collection/"
            f"dataStores/{data_store_id}/branches/0/documents:import"
        )

        auth_token = subprocess.check_output("gcloud auth print-access-token", shell=True, text=True).strip()

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        data = {"gcsSource": {"inputUris": [f"gs://{waize_gcs_uri}/*.jsonl"]}}

        response = requests.post(url, headers=headers, json=data, timeout=3600)

        if response.status_code == 200:
            print(f"Documents Import Job successfully started to Discovery Engine Data Store: {data_store_id}")
        else:
            print(f"Error importing documents: {response.status_code}, {response.text}")

        delay_factor = 2
        while True:
            if self.__import_finished(project_id, data_store_id, location):
                return data_store_id
            else:
                print(f"Documents Import Job is in progress, rechecking again in {delay_factor} seconds...")
                time.sleep(delay_factor)
                delay_factor = min(delay_factor**2, 300)

    def __app_exists(self, project_id, app_id, location) -> bool:
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") if location != "global" else None
        )
        client = discoveryengine.SearchServiceClient(client_options=client_options)
        serving_config = (
            f"projects/{project_id}/locations/{location}/"
            f"collections/default_collection/engines/{app_id}/"
            "servingConfigs/default_config"
        )
        try:

            content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(return_snippet=True),
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=5,
                    include_citations=True,
                    ignore_adversarial_query=True,
                    ignore_non_summary_seeking_query=True,
                    model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                        preamble="Here is an important question"
                    ),
                    model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                        version="stable",
                    ),
                ),
            )

            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query="What is the meaning of life?",
                page_size=10,
                filter='section_name: ANY("introduction")',
                content_search_spec=content_search_spec,
                query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                    condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
                ),
                spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                    mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
                ),
            )

            _ = client.search(request)
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(e)
            return False

    def __create_waize_app(self, project_id, dataset_name, data_store_id, location):
        """Creates a Vertex AI Search engine.

        Args:
            project_id (str): The Google Cloud project ID.
            dataset_name (str): A name to incorporate into the engine ID and display name.
            data_store_id (str): The ID of the data store to associate with the engine.

        Returns:
            str: The ID of the created engine.
        """
        print("Creating the VAIS endpoint...")
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        app_id = f"{dataset_name}-{random_suffix}"
        app_name = f"{dataset_name.capitalize()} Search App ({random_suffix})"

        auth_token = subprocess.check_output("gcloud auth print-access-token", shell=True, text=True).strip()

        url = (
            f"{self.base_url}/projects/{project_id}/locations/{location}/collections/"
            f"default_collection/engines?engineId={app_id}"
        )
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": project_id,
        }

        data = {
            "displayName": app_name,
            "dataStoreIds": [data_store_id],
            "solutionType": "SOLUTION_TYPE_SEARCH",
            "searchEngineConfig": {
                "searchTier": "SEARCH_TIER_ENTERPRISE",
                "searchAddOns": ["SEARCH_ADD_ON_LLM"],
            },
        }

        response = requests.post(url, headers=headers, json=data, timeout=3600)

        if response.status_code == 200:
            print(f"Discovery Engine Job '{app_name}' (ID: {app_id}) is launched successfully.")
        else:
            print(f"Error creating application: {response.status_code}, {response.text}")
        delay_factor = 2
        while True:
            if self.__app_exists(project_id, app_id, location):
                return app_id
            else:
                time.sleep(delay_factor)
                delay_factor = min(delay_factor**2, 300)
                print(f"Discovery Engine Job is in progress, rechecking again in {delay_factor} seconds...")


class VertexAIVectorStrategy(VectorStrategy):
    """Concrete implementation of VectorStrategy for using Vertex AI as the vector store."""

    DEPLOYED_INDEX_ID = "article_index_endpoint_deployed"
    ARTICLE_INDEX = "article_index"
    ARTICLE_INDEX_ENDPOINT = "article_index_endpoint"

    def __init__(self, storage_interface: Storage, config: dict[str, str], vectore_store_path: str) -> None:
        super().__init__(storage_interface, config)
        self.vectore_store_path = f"{vectore_store_path}_vertexai"

    def __create(self, embeddings: Embeddings, processed_files_dir: str):
        if not os.path.exists(self.vectore_store_path):
            print("Creating the directory...")
            os.makedirs(self.vectore_store_path)
        else:
            print("Removing & creating the directory...")
            shutil.rmtree(self.vectore_store_path, ignore_errors=True)
            os.makedirs(self.vectore_store_path)

        docs = self.storage_interface.process_directory(processed_files_dir, default_extract_data)
        all_jsons = {}
        for plan, documents in docs.items():
            store_path = os.path.join(self.vectore_store_path, plan)
            embs = embeddings.embed_documents([x.page_content for x in documents])
            embs_plan = [(f"{plan}_{i}", x) for i, x in enumerate(embs)]
            embs_df = pd.DataFrame(embs_plan, columns=["id", "embedding"])
            plan_output_jsonl = store_path + "_df.json"
            with open(plan_output_jsonl, "w", encoding="utf-8") as f:
                f.write(embs_df.to_json(orient="records", lines=True, force_ascii=False))
            all_jsons[plan] = plan_output_jsonl

        return all_jsons

    def create_bucket_and_copy(self, json_file, random_string):
        prefix = os.path.splitext(os.path.basename(json_file))[0]
        bucket_path = f"{prefix}-vertex-ai-search-{random_string}"
        client = storage.Client()
        bucket = client.bucket(bucket_path)
        bucket.location = "us-central1"
        bucket.create()

        blob = bucket.blob(os.path.basename(json_file))
        blob.upload_from_filename(json_file)
        return bucket_path

    def __copy(self, all_jsons):
        bucket_json_names = {}
        random_string = "".join(random.choices(string.ascii_lowercase, k=6))

        for plan, json_file in all_jsons.items():
            bucket_path = self.create_bucket_and_copy(json_file, random_string)
            print(f"File {json_file} copied to bucket: {bucket_path}")
            bucket_json_names[(json_file, plan)] = bucket_path

        return bucket_json_names

    def __deploy(self, bucket_json_names):
        deployed_endpoints = []
        random_string = "".join(random.choices(string.ascii_lowercase, k=4))
        for key, bucket_path in bucket_json_names.items():
            json_file, plan = key
            prefix = os.path.splitext(os.path.basename(json_file))[0]
            file_index_name = f"{prefix}_{self.ARTICLE_INDEX}_{random_string}"
            file_index_endpoint_name = f"{prefix}_{self.ARTICLE_INDEX_ENDPOINT}_{random_string}"
            file_index_deployed_name = f"{prefix}_{self.DEPLOYED_INDEX_ID}_{random_string}"

            file_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
                display_name=file_index_name,
                contents_delta_uri=f"gs://{bucket_path}/",
                dimensions=768,
                approximate_neighbors_count=10,
            )
            print(file_index)

            file_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=file_index_endpoint_name, public_endpoint_enabled=True
            )
            print(file_index_endpoint)

            file_index_endpoint.deploy_index(index=file_index, deployed_index_id=file_index_deployed_name)
            print(file_index_deployed_name)
            deployed_endpoints.append(
                DeployedEndpoint(file_index_name, file_index_endpoint.resource_name, file_index_deployed_name, plan)
            )

        endpoints_dir = f"{self.vectore_store_path}/endpoints"
        if not os.path.exists(endpoints_dir):
            os.makedirs(endpoints_dir)
        for endpoint in deployed_endpoints:
            endpoint_index = endpoint.index.replace("/", "_")
            with open(f"{endpoints_dir}/{endpoint_index}.txt", "w+", encoding="utf-8") as f:
                f.write(
                    "\n".join(
                        [
                            endpoint.index,
                            endpoint.index_endpoint_name,
                            endpoint.deployed_index_endpoint_name,
                            endpoint.plan,
                        ]
                    )
                )

        return deployed_endpoints

    def get_endpoints(self):
        deployed_endpoints = []
        endpoints_dir = f"{self.vectore_store_path}/endpoints"
        endpoint_files = glob.glob(endpoints_dir + "/*.txt")

        for endpoint_file in endpoint_files:
            with open(endpoint_file, "r+", encoding="utf-8") as f:
                endpoint_lines = f.readlines()
                endpoint_lines = [x.strip().replace("\n", "") for x in endpoint_lines]
                deployed_endpoint = DeployedEndpoint(
                    endpoint_lines[0], endpoint_lines[1], endpoint_lines[2], endpoint_lines[3]
                )
                deployed_endpoints.append(deployed_endpoint)
        return deployed_endpoints

    def get_vector_indices(
        self, regenerate: bool, embeddings: Embeddings, vector_indices: dict[str, str], processed_files_dir: str
    ):
        aiplatform.init()
        if not os.path.exists(self.vectore_store_path):
            all_jsons = self.__create(embeddings, processed_files_dir)
            bucket_json_names = self.__copy(all_jsons)
            deployed_endpoints = self.__deploy(bucket_json_names)
        else:
            deployed_endpoints = self.get_endpoints()

        docs = self.storage_interface.process_directory(processed_files_dir, default_extract_data)
        doc_mapping = InvertedIndex().build_map(docs)

        for deployed_endpoint in deployed_endpoints:
            real_endpoint_object = aiplatform.MatchingEngineIndexEndpoint(deployed_endpoint.index_endpoint_name)
            vector_store = VertexVectorStore(
                real_endpoint_object, deployed_endpoint.deployed_index_endpoint_name, embeddings, doc_mapping
            )
            vector_indices[deployed_endpoint.plan] = vector_store
        return vector_indices
