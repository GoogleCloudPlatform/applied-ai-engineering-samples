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
"""This module provides test to test module document_utils.py"""

from langchain.schema import Document

from gen_ai.common.document_utils import (
    build_doc_title,
    convert_dict_to_relevancies,
    convert_dict_to_summaries,
    convert_json_to_langchain,
    convert_langchain_to_json,
    generate_contexts_from_docs,
)
from gen_ai.deploy.model import QueryState


def test_convert_langchain_to_json():
    """Tests the conversion of a Document object to a JSON format.

    Verifies that the 'convert_langchain_to_json' function correctly translates the
    contents of a Document object, including page content and metadata, into a dictionary
    representing the JSON format.
    """
    doc = Document(page_content="This is a test document.", metadata={"summary": "This is a summary."})
    doc_json = convert_langchain_to_json(doc)
    assert doc_json["page_content"] == "This is a test document."
    assert doc_json["metadata"]["summary"] == "This is a summary."


def test_convert_json_to_langchain():
    """Tests the conversion of a JSON dictionary back to a Document object.

    Verifies that the 'convert_json_to_langchain' function correctly reconstitutes a
    Document object from a JSON dictionary format, preserving all content and metadata.
    """
    doc_json = {"page_content": "This is a test document.", "metadata": {"summary": "This is a summary."}}
    doc = convert_json_to_langchain(doc_json)
    assert doc.page_content == "This is a test document."
    assert doc.metadata["summary"] == "This is a summary."


def test_convert_dict_to_summaries():
    """Tests the extraction of summary information from a dictionary containing metadata.

    Verifies that the 'convert_dict_to_summaries' function correctly extracts summary-related
    metadata from a dictionary and forms a new summary dictionary.
    """
    doc = {
        "metadata": {"summary": "This is a summary.", "summary_reasoning": "This is the reasoning behind the summary."}
    }
    doc_json = convert_dict_to_summaries(doc)
    assert doc_json["summary"] == "This is a summary."
    assert doc_json["summary_reasoning"] == "This is the reasoning behind the summary."


def test_convert_dict_to_relevancies():
    """Tests the extraction of relevancy information from a dictionary containing metadata.

    Verifies that the 'convert_dict_to_relevancies' function correctly extracts relevancy-related
    metadata from a dictionary and forms a new relevancy dictionary.
    """
    doc = {"metadata": {"relevancy_score": 0.9, "relevancy_reasoning": "This is the reasoning behind the relevancy."}}
    doc_json = convert_dict_to_relevancies(doc)
    assert doc_json["relevancy_score"] == 0.9
    assert doc_json["relevancy_reasoning"] == "This is the reasoning behind the relevancy."


def test_build_doc_title():
    """Tests the construction of a document title from given metadata.

    Verifies that the 'build_doc_title' function correctly concatenates various elements of metadata
    into a structured document title string.
    """
    metadata = {"set_number": "1", "section_name": "Section 1", "doc_identifier": "Doc 1", "policy_number": "Policy 1"}
    doc_title = build_doc_title(metadata)
    assert doc_title == "1 Section 1 Doc 1 Policy 1 "


def test_generate_contexts_from_docs_custom_case_1():
    """Tests the generation of context strings from a list of documents based on a given query state.

    Verifies that the 'generate_contexts_from_docs' function properly creates context strings for
    each document, appending the necessary headers, and updates the query state with the number of
    documents used and the relevancy scores associated with used sections.
    """
    docs = [
        Document(
            page_content="This is a test document.",
            metadata={
                "section_name": "Section 1",
                "summary": "This is a summary.",
                "relevancy_score": 0.9,
                "set_number": "1",
                "doc_identifier": "Doc 1",
                "policy_number": "Policy 1",
                "original_filepath": "test_file.txt",
            },
        )
    ]
    query_state = QueryState(
        question="What is the purpose of the document?",
        answer="To provide information.",
        additional_information_to_retrieve="",
        all_sections_needed=[],
    )
    contexts = generate_contexts_from_docs(docs, query_state)
    assert (
        contexts[0]
        == "\nDOCUMENT TITLE: 1 Section 1 Doc 1 Policy 1 \nDOCUMENT CONTENT: This is a test document.\n------------\n\n"
    )
    assert query_state.num_docs_used == [1]
    assert query_state.used_articles_with_scores == [("Section 1 Context: 1", 0.9)]


def test_generate_contexts_from_docs_custom_case_2():
    """Tests the generation of context strings from a list of documents based without any query_state.

    Verifies that the 'generate_contexts_from_docs' function properly creates context strings for
    each document, appending the necessary headers, and updates the query state with the number of
    documents used and the relevancy scores associated with used sections.
    """
    docs = [
        Document(
            page_content="This is a test document.",
            metadata={
                "section_name": "Section 1",
                "summary": "This is a summary.",
                "relevancy_score": 0.9,
                "set_number": "1",
                "doc_identifier": "Doc 1",
                "policy_number": "Policy 1",
                "original_filepath": "test_file.txt",
            },
        )
    ]
    contexts = generate_contexts_from_docs(docs)
    assert (
        contexts[0]
        == "\nDOCUMENT TITLE: 1 Section 1 Doc 1 Policy 1 \nDOCUMENT CONTENT: This is a test document.\n------------\n\n"
    )
