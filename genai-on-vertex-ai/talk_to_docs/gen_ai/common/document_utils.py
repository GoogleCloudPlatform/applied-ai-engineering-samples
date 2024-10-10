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
"""This module provides functions for converting documents to Langchain and dictionaries, as well as
generation of contexts from the list of docs"""

from langchain.schema import Document

from typing import Any

def convert_langchain_to_json(doc: Document) -> dict[str, Any]:
    """
    Converts a `Document` object to a JSON-serializable dictionary.

    This function is specifically designed for converting documents from the custom `Document`
    format used within the langchain schema to a JSON format for storage or further processing.

    Args:
        doc (Document): The `Document` object to convert.

    Returns:
        dict: A dictionary representation of the `Document`, suitable for JSON serialization.
    """
    doc_json = {}
    doc_json["page_content"] = doc.page_content
    doc_json["metadata"] = doc.metadata
    return doc_json


def convert_json_to_langchain(doc: dict[str, Any]) -> Document:
    """
    Converts a JSON-serializable dictionary to a `Document` object.

    This function allows for the reverse operation of `convert_langchain_to_json`, enabling
    the reconstruction of a `Document` object from its JSON dictionary representation.

    Args:
        doc (dict): The dictionary representation of a `Document`.

    Returns:
        Document: The reconstructed `Document` object.
    """
    return Document(page_content=doc["page_content"], metadata=doc["metadata"])


def convert_dict_to_summaries(doc: dict) -> dict[str, Any]:
    """
    Converts a `Document` object to a JSON-serializable dictionary.

    This function is specifically designed for converting documents from the custom `Document`
    format used within the langchain schema to a JSON format for storage or further processing.

    Args:
        doc (Document): The `Document` object to convert.

    Returns:
        dict: A dictionary representation of the `Document`, suitable for JSON serialization.
    """
    doc_json = {}
    doc_json["summary"] = doc["metadata"]["summary"]
    doc_json["summary_reasoning"] = doc["metadata"]["summary_reasoning"]
    return doc_json


def convert_dict_to_relevancies(doc: dict) -> dict[str, Any]:
    """
    Converts a `Document` object to a JSON-serializable dictionary.

    This function is specifically designed for converting documents from the custom `Document`
    format used within the langchain schema to a JSON format for storage or further processing.

    Args:
        doc (Document): The `Document` object to convert.

    Returns:
        dict: A dictionary representation of the `Document`, suitable for JSON serialization.
    """
    doc_json = {}
    doc_json["relevancy_score"] = doc["metadata"]["relevancy_score"]
    doc_json["relevancy_reasoning"] = doc["metadata"]["relevancy_reasoning"]
    return doc_json
