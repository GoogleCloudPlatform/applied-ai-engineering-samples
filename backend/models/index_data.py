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

from typing import Literal, Union
from pydantic import BaseModel, HttpUrl


# Data Processing Pipeline input data model
class GCSInputConfig(BaseModel):
  project_name: str
  bucket_name: str
  prefix: str


class URLInputConfig(BaseModel):
  url: HttpUrl


InputConfig = Union[GCSInputConfig, URLInputConfig]


class Input(BaseModel):
  type: Literal["gcs", "url"]
  config: InputConfig


# Data Processing Pipeline input loader data model
class DataLoaderConfig(BaseModel):
  project_id: str
  location: str
  processor_name: str
  gcs_output_path: str


class DataLoader(BaseModel):
  type: Literal["document_ai"]
  config: DataLoaderConfig


# Data Processing Pipeline input splitter data model
class RecursiveCharacterTextSplitterConfig(BaseModel):
  chunk_size: int
  chunk_overlap: int


class CharacterTextSplitterConfig(BaseModel):
  chunk_size: int
  chunk_overlap: int


SplitterConfig = Union[
    RecursiveCharacterTextSplitterConfig, CharacterTextSplitterConfig
]


class DocumentSplitter(BaseModel):
  type: Literal["recursive_character", "character"]
  config: SplitterConfig


# Data Processing Pipeline input vector store
class VertexAIVectorStoreConfig(BaseModel):
  project_id: str
  region: str
  index_id: str
  endpoint_id: str
  embedding_model: str
  index_name: str


class GenericVectorStoreConfig(BaseModel):
  index_name: str


VectorStoreConfig = Union[VertexAIVectorStoreConfig, GenericVectorStoreConfig]


class VectorStore(BaseModel):
  type: Literal["vertex_ai"]
  config: VectorStoreConfig


# Data Processing Pipeline overall message
class PubSubMessage(BaseModel):
  input: Input
  data_loader: DataLoader
  document_splitter: DocumentSplitter
  vector_store: VectorStore
