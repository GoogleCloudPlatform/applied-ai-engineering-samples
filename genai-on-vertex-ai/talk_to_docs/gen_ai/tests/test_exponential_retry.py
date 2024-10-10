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
from gen_ai.common.exponential_retry import LLMExponentialRetryWrapper, timeout_llm_call
import pytest
from unittest.mock import Mock, patch
from google.api_core.exceptions import InternalServerError
from time import sleep


def test_successful_execution_no_retry():
    mock_chain = Mock()
    mock_chain.run.return_value = "Success"
    wrapper = LLMExponentialRetryWrapper(mock_chain)

    assert wrapper.run("test") == "Success"
    mock_chain.run.assert_called_once_with("test")


def test_retry_logic_on_failure():
    mock_chain = Mock()
    mock_chain.run.side_effect = [InternalServerError("Temporary error"), "Success"]

    wrapper = LLMExponentialRetryWrapper(mock_chain)
    with patch("time.sleep") as mock_sleep:
        assert wrapper.run("test") == "Success"

    assert mock_chain.run.call_count == 2
    mock_sleep.assert_called_once()


def test_max_retry_exceeded():
    mock_chain = Mock()
    mock_chain.run.side_effect = InternalServerError("Persistent error")

    wrapper = LLMExponentialRetryWrapper(mock_chain)
    with patch("time.sleep"), pytest.raises(Exception) as exc_info:
        wrapper.run("test")

    assert "failed after 15 retries" in str(exc_info.value)
    assert mock_chain.run.call_count == 15


def test_timeout_decorator_success():
    """
    Tests if the `timeout_llm_call` decorator works as expected when the decorated 
    function completes within the specified timeout.
    """

    @timeout_llm_call(timeout=10)
    def mock_function():
        return "Success"
    result = mock_function()

    assert result=="Success"


def test_timeout_decorator_exceed_timeout():
    """
    Tests the `timeout_llm_call` decorator's handling of timeouts.

    Verifies that a function exceeding the specified timeout is interrupted,
    and the returned result is as expected:
    - `score` is 0.
    - `result` contains the expected "answer" key.
    - `result["answer"]` is the expected timeout message.
    """

    @timeout_llm_call(timeout=0.1)
    def mock_function(*args, **kwargs):
        sleep(1) 
        return "This should not be returned"

    result, score = mock_function()
    assert score == 0
    assert "answer" in result
    assert result["answer"]=="I was not able to answer this question"
