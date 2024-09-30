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

import json
import logging
from typing import Sequence, Tuple
import apache_beam as beam
from langchain_core.documents import Document
from langchain_google_vertexai import (
    VectorSearchVectorStoreDatastore,
    VertexAIEmbeddings,
)
from langchain_google_vertexai.vectorstores._sdk_manager import VectorSearchSDKManager
from langchain_google_vertexai.vectorstores.document_storage import (
    DataStoreDocumentStorage,
    DocumentStorage,
)


class UpsertToVectorSearchFn(beam.DoFn):
  """DoFn for upserting documents to Vector Search."""

  def setup(self):
    self.vector_stores = {}
    self.datastore_clients = {}

  def process(self, element):
    """Process and upsert documents to Vector Search.

    Args:
        element (tuple): A tuple containing the document key and the
          document(s).

    Yields:
        str: A status message indicating the result of the upsert operation.
    """
    key, docs = element
    try:
      if not isinstance(docs, list):
        docs = [docs]

      base_element = docs[0].metadata["base_element"]
      vector_store_config = base_element["vector_store"]["config"]

      if key not in self.vector_stores:
        DATASTORE_DB_NAME = ""

        sdk_manager = VectorSearchSDKManager(
            project_id=vector_store_config["project_id"],
            region=vector_store_config["region"],
        )

        self.datastore_clients[key] = sdk_manager.get_datastore_client(
            database=DATASTORE_DB_NAME
        )

        self.vector_stores[key] = (
            VectorSearchVectorStoreDatastore.from_components(
                project_id=vector_store_config["project_id"],
                region=vector_store_config["region"],
                index_id=vector_store_config["index_id"],
                endpoint_id=vector_store_config["endpoint_id"],
                embedding=VertexAIEmbeddings(
                    model_name=vector_store_config["embedding_model"]
                ),
                stream_update=True,
            )
        )

        class CustomDataStoreDocumentStorage(
            DataStoreDocumentStorage, DocumentStorage
        ):

          def mset(
              self, key_value_pairs: Sequence[Tuple[str, Document]]
          ) -> None:
            logging.info("setting override mset")
            ids = [key for key, _ in key_value_pairs]
            documents = [document for _, document in key_value_pairs]

            with self._client.transaction():
              keys = [self._client.key(self._kind, id_) for id_ in ids]
              entities = []
              for key, document in zip(keys, documents):
                entity = self._client.entity(
                    key=key,
                    exclude_from_indexes=(
                        self._text_property_name,
                        self._metadata_property_name,
                    ),
                )
                entity[self._text_property_name] = document.page_content
                entity[self._metadata_property_name] = document.metadata
                entities.append(entity)

              self._client.put_multi(entities)

        self.vector_stores[key]._document_storage = (
            CustomDataStoreDocumentStorage(
                datastore_client=self.datastore_clients[key]
            )
        )

      vector_store = self.vector_stores[key]

      texts = [doc.page_content for doc in docs]

      # Modify the metadata
      metadatas = []
      for doc in docs:
        metadata = (
            doc.metadata.copy()
        )  # Create a copy to avoid modifying the original
        if "base_element" in metadata:
          del metadata["base_element"]  # Remove base_element
        metadata["index_name"] = vector_store_config.get(
            "index_name"
        )  # Add index_name
        metadatas.append(metadata)

      logging.info(
          f"Preparing to upsert {len(texts)} texts for document: {key}"
      )
      logging.info(f"First text (truncated to 200 chars): {texts[0][:200]}")
      logging.info(f"First metadata: {json.dumps(metadatas[0], indent=2)}")

      vector_store.add_texts(
          texts=texts,
          metadatas=metadatas,
          is_complete_overwrite=False,
      )
      logging.info(
          f"Successfully upserted {len(texts)} splits for document: {key}"
      )
      yield (True, base_element)
    except Exception as e:
      logging.error(
          f"Error upserting to Vector Search for document {key}: {str(e)}"
      )
      logging.exception("Full traceback:")
      yield (False, base_element)
