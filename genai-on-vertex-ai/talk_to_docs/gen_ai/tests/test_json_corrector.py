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
import pytest
from gen_ai.common.ioc_container import Container
import json5


@pytest.fixture
def json_corrector_chain():
    return Container.json_corrector_chain()


@pytest.fixture
def corrupted_json():
    return """
     {
      "plan_and_summaries": "I have the information on how to perform a stock adjustment in GROCERIES...",
      "additional_sections_to_retrieve": ["4.7 --- Metro Markdown Matrix - A4 Reference Card (MAY 23)"],
      "answer": "To perform a stock adjustment in GROCERIES, you can either use the RF device or Store Central...",
      "confidence_score": 80,
      "context_used": "1.9 --- Action Stock Adjustment"
    }
    ```
    """


@pytest.fixture
def expected_json_str():
    return """
     {
      "plan_and_summaries": "I have the information on how to perform a stock adjustment in GROCERIES...",
      "additional_sections_to_retrieve": ["4.7 --- Metro Markdown Matrix - A4 Reference Card (MAY 23)"],
      "answer": "To perform a stock adjustment in GROCERIES, you can either use the RF device or Store Central...",
      "confidence_score": 80,
      "context_used": "1.9 --- Action Stock Adjustment"
    }
    """


def test_correct_corrupted_json(json_corrector_chain, corrupted_json, expected_json_str):
    actual_output = json_corrector_chain.run(json=corrupted_json)
    actual_json = json5.loads(actual_output)
    expected_json = json5.loads(expected_json_str)
    assert actual_json == expected_json
