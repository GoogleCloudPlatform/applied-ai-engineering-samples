# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from typing import Any, Dict, List, Optional

from flask import jsonify
import functions_framework
from google.cloud import firestore
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    Namespace,
)
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, chain
from langchain_google_community.vertex_rank import VertexAIRank
from langchain_google_vertexai import (
    VectorSearchVectorStoreDatastore,
    VertexAI,
    VertexAIEmbeddings,
)
import nest_asyncio


PROJECT_ID = os.environ.get(
    "PROJECT_ID", "Specified environment variable is not set."
)


# Configure logging
def log(message: str, level: str = "INFO") -> None:
  print(f"[{level}] {message}", file=sys.stdout)


# db = firestore.Client(database="rp-index-store")
db = firestore.Client()

nest_asyncio.apply()

DEFAULT_PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
Question:
{query}
Answer:
"""

embedding_function = VertexAIEmbeddings(model_name="text-embedding-004")


def prepare_filter(filters: Any = {}) -> Optional[List[Namespace]]:
  """Prepare filters for Vertex AI Vector Search."""
  log(f"Preparing filters: {filters}")
  return (
      [
          Namespace(name=key, allow_tokens=[value])
          for key, value in filters.items()
      ]
      if filters
      else None
  )


def get_vector_store_details(index_name: str) -> Any:
  """Retrieve vector store details from Firestore."""
  log(f"Retrieving vector store details for index: {index_name}")
  doc_ref = db.collection("rp_indices").document(index_name)
  doc = doc_ref.get()
  if doc.exists:
    vector_store = doc.to_dict().get("vector_store", {})
    log(f"Vector store details retrieved: {vector_store}")
    return vector_store
  else:
    log(f"No document found for index_name: {index_name}")
    raise ValueError(f"No document found for index_name: {index_name}")


def get_retriever(
    vectordb: Any,
    retriever_name: str,
    llm: Any,
    search_kwargs: Dict[str, Any],
    is_rerank: bool,
) -> Any:
  """Get the appropriate retriever based on the retriever name and rerank flag."""
  log(f"Getting retriever: {retriever_name}, Rerank: {is_rerank}")

  basic_retriever_map = {
      "TopK": lambda: vectordb.as_retriever(search_kwargs=search_kwargs),
      "MultiQueryRetriever": lambda: MultiQueryRetriever.from_llm(
          retriever=vectordb.as_retriever(search_kwargs=search_kwargs), llm=llm
      ),
      "ContextualCompressionRetriever": lambda: ContextualCompressionRetriever(
          base_compressor=LLMChainFilter.from_llm(llm),
          base_retriever=vectordb.as_retriever(search_kwargs=search_kwargs),
      ),
  }

  basic_retriever_func = basic_retriever_map.get(retriever_name)
  if not basic_retriever_func:
    log(f"Invalid retriever name: {retriever_name}")
    raise ValueError(f"Invalid retriever name: {retriever_name}")

  basic_retriever = basic_retriever_func()

  if is_rerank:
    reranker = VertexAIRank(
        project_id=PROJECT_ID,
        ranking_config="default_ranking_config",
        title_field="source",
        top_n=5,
    )
    return ContextualCompressionRetriever(
        base_compressor=reranker, base_retriever=basic_retriever
    )
  else:
    return basic_retriever


def get_vectordb(vector_store_type: str, vector_store_details: Any) -> Any:
  """Get the appropriate vector database based on the vector store type."""
  log(f"Getting vector database: {vector_store_type}")
  vectordb_map = {
      "VectorSearchVectorStoreDatastore": (
          lambda: VectorSearchVectorStoreDatastore.from_components(
              project_id=vector_store_details.get("project_id"),
              region=vector_store_details.get("region"),
              index_id=vector_store_details.get("index_id"),
              endpoint_id=vector_store_details.get("endpoint_id"),
              embedding=embedding_function,
              stream_update=True,
          )
      ),
      # Add more vector store types here as needed
  }
  vectordb_func = vectordb_map.get(vector_store_type)
  if vectordb_func:
    return vectordb_func()
  else:
    log(f"Invalid vector store type: {vector_store_type}")
    raise ValueError(f"Invalid vector store type: {vector_store_type}")


def create_rag_answer(
    retriever: Any, query: str, llm: VertexAI, prompt_template: str
) -> Any:
  """Create a RAG (Retrieval-Augmented Generation) answer."""
  prompt = PromptTemplate(
      template=prompt_template, input_variables=["context", "query"]
  )
  setup_and_retrieval = RunnableParallel(
      {"context": retriever, "query": RunnablePassthrough()}
  )

  @chain
  def qa_chain(query: str) -> Any:
    retrieved_context = setup_and_retrieval.invoke(query)
    create_answer = prompt | llm
    answer = create_answer.invoke(retrieved_context)
    return answer, retrieved_context

  answer, retrieved_context = qa_chain.invoke(query)
  log(f"Generated answer: {answer}")
  return answer, retrieved_context


@functions_framework.http
def execute_rag_query(request) -> Any:
  """Execute a RAG (Retrieval-Augmented Generation) query based on the provided request."""
  try:
    request_data = request.get_json()
    retriever_name = request_data["retriever_name"]
    query = request_data["query"]
    model_name = request_data["model_name"]
    model_params = request_data.get("model_params", {})
    index_name = request_data["index_name"]
    vector_store_type = request_data.get(
        "vector_store_type", "VectorSearchVectorStoreDatastore"
    )
    prompt_template = request_data.get(
        "prompt_template", DEFAULT_PROMPT_TEMPLATE
    )
    is_rerank = request_data.get("is_rerank", False)
    log(f"Executing RAG query: {query}")
    log(
        f"Retriever: {retriever_name}, Model: {model_name}, Index:"
        f" {index_name}, Rerank: {is_rerank}"
    )

    vector_store_details = get_vector_store_details(index_name)
    llm = VertexAI(model_name=model_name, **model_params)
    vectordb = get_vectordb(vector_store_type, vector_store_details)

    filters = {"index_name": index_name}
    search_kwargs = {"filter": prepare_filter(filters)}

    retriever = get_retriever(
        vectordb=vectordb,
        retriever_name=retriever_name,
        llm=llm,
        search_kwargs=search_kwargs,
        is_rerank=is_rerank,
    )
    rag_response, retrieved_context = create_rag_answer(
        retriever=retriever,
        query=query,
        llm=llm,
        prompt_template=prompt_template,
    )

  except Exception as e:
    log(f"Error executing RAG query: {str(e)}")
    return jsonify({"error": str(e)}), 500

  else:
    log("RAG query executed successfully")
    return jsonify({
        "query": query,
        "answer": rag_response,
        "context": str(retrieved_context.get("context")),
    })
