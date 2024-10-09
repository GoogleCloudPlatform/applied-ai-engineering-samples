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
"""This module provides functions for measuring execution time and logging system metrics."""

from gen_ai.common.ioc_container import Container


from timeit import default_timer


def trace_on(msg: str, measure_time: bool = False):
    """Decorates a function to log its execution details, with an optional execution time measurement.

    This decorator adds logging functionality to any function it decorates. It logs a specified message before
    and after the function's execution. Optionally, it can also measure and log the execution time of the function.
    If the `Container`'s configuration is set to print system metrics, it logs the message or execution time
    using the `Container`'s logger.

    Args:
        msg: A string message to log before and after the decorated function's execution.
        measure_time: A boolean flag to indicate whether the execution time should be measured and logged.
            Defaults to False.

    Returns:
        A callable object that replaces the decorated function, adding the logging functionality.

    Example:
        @trace_on("Generating report")
        def generate_report(data):
            # Function body here
            pass

        @trace_on("Training model", measure_time=True)
        def train_model(data):
            # Function body here
            pass
    """

    def decorator(function):
        def rho_aias(*args, **kwargs):
            start = default_timer()
            result = function(*args, **kwargs)
            end = default_timer()

            output_msg = msg
            if measure_time:
                output_msg = f"{output_msg} took {end - start} seconds"

            if "print_system_metrics" in Container.config and Container.config["print_system_metrics"]:
                Container.logger().info(msg=output_msg)
            return result

        return rho_aias

    return decorator
