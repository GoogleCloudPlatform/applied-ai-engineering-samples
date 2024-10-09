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
"""This module implements Embedding Provider, in case if user wants to specify 
Vertex AI Embeddings or OpenAIEmbeddings"""

from langchain.schema.embeddings import Embeddings
from langchain.embeddings import VertexAIEmbeddings, OpenAIEmbeddings


class EmbeddingsProvider:
    """Provides embeddings based on the specified embeddings service.

    This class serves as a factory for creating instances of embedding classes based on the specified service. 
    It currently supports creating embeddings from either 'openai' or 'vertexai'.

    Attributes:
        embeddings_name (str): The name of the embeddings service. It determines which embeddings class to instantiate.
        embeddings_model_name (str, optional): The specific model name for the embeddings service if applicable. 
        Default is None.

    Raises:
        ValueError: If the specified embeddings service is not supported.

    Returns:
        Embeddings: An instance of a class that provides embeddings functionalities based on the specified service.
    """
    def __init__(self, embeddings_name, embeddings_model_name: str = None):
        self.embeddings_name = embeddings_name
        self.embeddings_model_name = embeddings_model_name

    def __call__(self) -> Embeddings:
        """Returns the Embeddings class

        Raises:
            ValueError: currently supports openai and vertexai embeddings. Raises exception if other types are 
            specified

        Returns:
            Embeddings: langchain class of base embeddings
        """
        print(f"Loading {self.embeddings_name} Embeddings...")
        if "vertexai" in self.embeddings_name:
            return VertexAIEmbeddings(model_name=self.embeddings_model_name)
        elif "openai" in self.embeddings_name:
            return OpenAIEmbeddings()
        else:
            raise ValueError("Not supported embeddings name in config")
