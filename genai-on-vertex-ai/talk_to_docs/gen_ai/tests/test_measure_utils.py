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
"""This module provides tests for measure_utils.py"""

from unittest.mock import patch
from gen_ai.common.measure_utils import trace_on
from gen_ai.common.ioc_container import Container


def test_trace_on_logging():
    """Test the trace_on decorator for proper logging without execution time measurement."""
    with patch("gen_ai.common.ioc_container.Container.logger") as mock_logger:
        Container.config["print_system_metrics"] = True

        @trace_on("Testing function execution")
        def test_function():
            return "Function executed"

        result = test_function()

        assert result == "Function executed"

        mock_logger().info.assert_called_with(msg="Testing function execution")


def test_trace_on_with_time_measurement():
    """Test the trace_on decorator for correct execution time measurement and logging."""
    with patch("gen_ai.common.ioc_container.Container.logger") as mock_logger:
        Container.config["print_system_metrics"] = True

        @trace_on("Timing function", measure_time=True)
        def test_function():
            return "Function executed"

        # Call the decorated function
        result = test_function()

        # Check that the function returns the correct result
        assert result == "Function executed"

        # Assert that the log message contains the expected text
        assert mock_logger().info.call_args.startswith("Timing function took")
        # Additionally, you could use a regex to assert more precisely that it logs a time.
