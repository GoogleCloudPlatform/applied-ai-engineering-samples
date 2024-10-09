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
from unittest.mock import MagicMock, patch

import pytest
from langchain.docstore.document import Document

from gen_ai.common.ioc_container import Container
from gen_ai.common.react_utils import (
    get_confidence_score,
    score_document,
    summarize_document,
    score_retrieved_documents,
    summarize_and_score_documents,
)


def test_get_confidence_score_high():
    question = "What is the capital of France?"
    answer = "The capital of France is Paris."
    confidence = get_confidence_score(question, answer)
    assert confidence >= 5


def test_get_confidence_score_low():
    question = "What is the capital of France?"
    answer = "I was not able to find an information about the capital of France"
    confidence = get_confidence_score(question, answer)
    assert confidence <= 1


@pytest.fixture
def enable_relevancy_score():
    original_setting = Container.config.get("use_relevancy_score", False)
    Container.config["use_relevancy_score"] = True
    yield
    Container.config["use_relevancy_score"] = original_setting


def test_score_document_high(enable_relevancy_score):
    retriever_scoring_chain = Container.retriever_scoring_chain()
    json_corrector_chain = Container.json_corrector_chain()
    aspect_based_summary_chain = Container.aspect_based_summary_chain()

    question = "What is the capital of France?"
    page = "In this document we talk about geography. For example, the capital of Italy is Rome. And also the capital of France is Paris."
    doc = Document(page_content=page)

    index, doc = summarize_document(doc, 1, question, aspect_based_summary_chain, json_corrector_chain)
    index, doc = score_document(doc, 1, question, retriever_scoring_chain, json_corrector_chain)

    assert index == 1, "Index must be the same as the document index"
    assert doc.metadata["relevancy_score"] >= 5, "Document must be very relevant"


def test_score_document_low():
    retriever_scoring_chain = Container.retriever_scoring_chain()
    json_corrector_chain = Container.json_corrector_chain()
    question = "What is the capital of France?"
    page = "In this document we talk about biology. For example, the gemini Panteras consists of 5 species: tiger, lion, leopard, jaguar and snow leopard. Cheetah is not a Pantera."
    doc = Document(page_content=page)
    index, doc = score_document(doc, 1, question, retriever_scoring_chain, json_corrector_chain)

    assert index == 1, "Index must be the same as the document index"
    assert doc.metadata["relevancy_score"] <= 1, "Document must be very irrelevant"


@patch("gen_ai.common.react_utils.score_document")
@patch("gen_ai.common.ioc_container.Container.retriever_scoring_chain")
@patch("gen_ai.common.ioc_container.Container.json_corrector_chain")
def test_score_retrieved_documents_order_preserved(
    mock_json_corrector_chain, mock_retriever_scoring_chain, mock_score_document
):
    mock_retriever_scoring_chain.return_value = MagicMock()
    mock_json_corrector_chain.return_value = MagicMock()

    # Mock score_document to return different scores for each document, but in a predictable manner
    # The score is simply the document index * 10 for differentiation
    def side_effect(doc, index, question, retriever_scoring_chain, json_corrector_chain):
        doc.metadata["relevancy_score"] = index * 10
        return index, doc

    mock_score_document.side_effect = side_effect

    docs = [Document(page_content=f"Content {i}") for i in range(5)]
    question = "What is the relevance?"

    expected_scores_and_reasonings = [i * 10 for i in range(5)]

    scored_docs = score_retrieved_documents(docs, question)
    scores = [doc.metadata["relevancy_score"] for doc in scored_docs]

    assert scores == expected_scores_and_reasonings, "Document scores are not in the expected order."


@pytest.fixture
def mock_docs_and_scores():
    return [
        Document(page_content="Doc 1", metadata={"relevancy_score": 40, "summary": "Doc 1"}),
        Document(page_content="Doc 2", metadata={"relevancy_score": 60, "summary": "Doc 2"}),
        Document(page_content="Doc 3", metadata={"relevancy_score": 80, "summary": "Doc 3"}),
    ]


@patch("gen_ai.common.react_utils.score_retrieved_documents")
@patch("gen_ai.common.react_utils.summarize_retrieved_documents")
def test_filters_out_below_threshold(mock_summarize, mock_score, mock_docs_and_scores, enable_relevancy_score):
    mock_summarize.return_value = mock_docs_and_scores
    mock_score.return_value = mock_docs_and_scores

    question = "What is the impact?"
    filtered_docs = summarize_and_score_documents(mock_docs_and_scores, question, threshold=50)
    assert len(filtered_docs) == 2, "Should only return 2 documents"
    assert all(doc.metadata["relevancy_score"] >= 50 for doc in filtered_docs)


@patch("gen_ai.common.react_utils.score_retrieved_documents")
@patch("gen_ai.common.react_utils.summarize_retrieved_documents")
def test_returns_only_above_threshold(mock_summarize, mock_score, mock_docs_and_scores, enable_relevancy_score):
    mock_summarize.return_value = mock_docs_and_scores
    mock_score.return_value = mock_docs_and_scores

    question = "What is the impact?"
    filtered_docs = summarize_and_score_documents(mock_docs_and_scores, question, threshold=50)

    for doc in filtered_docs:
        assert doc.metadata["relevancy_score"] >= 50
