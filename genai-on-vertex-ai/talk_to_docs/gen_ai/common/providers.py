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
"""

from gen_ai.common.document_retriever import SemanticDocumentRetriever
from gen_ai.custom_client_functions import CustomSemanticDocumentRetriever


class DocumentRetrieverProvider:
    def __call__(self, name: str) -> "DocumentRetriever":
        if name == "semantic":
            return SemanticDocumentRetriever()
        elif name == "custom":
            return CustomSemanticDocumentRetriever()
        else:
            raise ValueError("Not implemented document retriver")
