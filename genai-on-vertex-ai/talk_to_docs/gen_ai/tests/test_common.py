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
from gen_ai.common.common import merge_outputs, split_large_document

def test_document_not_exceeding_threshold():
    document = "This is a short document."
    threshold = 100  # Well above the word count of the document
    expected = [(document, len(document))]
    assert split_large_document(document, threshold) == expected

def test_document_meeting_threshold_exactly():
    document = "This is exactly five words."
    threshold = 5  # Exactly the word count of the document
    # Adjusting for tokens might cause an unexpected split, depending on your implementation
    expected_length = 1  # Expecting the document not to be split
    result = split_large_document(document, threshold)
    assert len(result) == expected_length
    assert sum(len(x[0]) for x in result) == len(document)

def test_document_exceeding_threshold():
    document = "This document. Exceeds the specified threshold. It should be split."
    threshold = 5  # Lower threshold to force splitting
    result = split_large_document(document, threshold)
    assert len(result) > 1  # Expecting multiple pieces
    for piece, length in result:
        assert length == len(piece)  # Ensure length is correctly calculated

def test_document_with_long_sentence():
    document = "This is a very long sentence that by itself exceeds the threshold, which should result in it being its own segment despite the threshold."
    threshold = 10  # Set a low threshold to test splitting on long sentences
    result = split_large_document(document, threshold)
    assert len(result) == 1  # Expecting only one piece since it's one sentence
    assert result[0][0] == document  # The content should match the original document

def test_merge_with_high_confidence():
    """Test that the output with 100 confidence score is returned immediately."""
    outputs = [
        ({"answer": "A", "context_used": ""}, 90),
        ({"answer": "B", "context_used": "Context B"}, 100),
        ({"answer": "C", "context_used": "Context C"}, 80)
    ]
    result, confidence, index = merge_outputs(outputs)
    assert confidence == 100
    assert result["answer"] == "B"
    assert index == 1

def test_merge_different_keys():
    """Test merging outputs with various keys."""
    outputs = [
        ({"plan_and_summaries": "Plan A", "additional_sections_to_retrieve": "Section A", "context_used": ["Context A"], "answer": "A"}, 80),
        ({"plan_and_summaries": "Plan B", "additional_sections_to_retrieve": "Section B", "context_used": ["Context B"], "answer": "B"}, 85)
    ]
    result, confidence, index = merge_outputs(outputs)
    assert result["plan_and_summaries"] == "Plan APlan B"
    assert result["additional_sections_to_retrieve"] == "Section ASection B"
    assert "Context A" in result["context_used"] and "Context B" in result["context_used"]
    assert result["answer"] == "B"
    assert confidence == 85
    assert index == 1

def test_empty_outputs():
    """Test handling of empty outputs list."""
    outputs = []
    result = merge_outputs(outputs)
    assert result == (None, 0, -1), "Expected a tuple with None, 0, and -1 for empty inputs"
