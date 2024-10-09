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
"""
This module implements functionality to automatically retry functions with exponential backoff, 
targeting operations that might intermittently fail due to transient issues such as network 
connectivity or server availability. It provides a decorator that can be used to wrap any 
function that requires retrying upon encountering specific exceptions like internal server errors 
or API call errors.

The main components include:
- A decorator `retry_with_exponential_backoff` which adds retry logic to functions. This is 
  useful for handling operations that may temporarily fail by retrying them with increasing 
  delays.
- A class `LLMExponentialRetryWrapper` which wraps instances of `LLMChain` to apply the retry 
  decorator to their `run` method, enabling retries with exponential backoff for methods that 
  execute potentially unstable operations.

Classes:
    LLMExponentialRetryWrapper: Enhances an `LLMChain` with automatic retry capabilities on its `run` method.

Functions:
    retry_with_exponential_backoff(max_retries=15, initial_delay=2, backoff_factor=2): Decorator that 
    retries a function upon encountering specified exceptions, with the delay between retries 
    increasing exponentially.

Usage:
    The decorator can be applied directly to functions that may experience transient failures, and
    the wrapper class can be used to enhance objects by encapsulating them to add retry capabilities.

Examples:
    Using the retry decorator:
        @retry_with_exponential_backoff(max_retries=3, initial_delay=1, backoff_factor=2)
        def some_function():
            # Implementation details

    Using the wrapper class:
        chain_instance = LLMChain()
        retry_wrapper = LLMExponentialRetryWrapper(chain_instance)
        result = retry_wrapper.run()

Exceptions Handled:
    InternalServerError: Handled during retries when a function raises this due to server-side issues.
    GoogleAPICallError: Handled during retries for errors related to Google API calls.
"""

import functools
import time
from func_timeout import func_timeout, FunctionTimedOut

from google.api_core.exceptions import GoogleAPICallError, InternalServerError
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Any


def retry_with_exponential_backoff(max_retries=15, initial_delay=2, backoff_factor=2):
    """
    A decorator for adding retry logic with exponential backoff to functions.

    This decorator will attempt to run a function and, if it fails with an exception,
    retry the function call. The delay between retries increases exponentially based
    on the backoff_factor. This is particularly useful for operations that might fail
    temporarily (e.g., network operations, temporary resource unavailability).

    Args:
        max_retries (int, optional): Maximum number of retries. Defaults to 3.
        initial_delay (int or float, optional): The initial delay in seconds before the first retry. Defaults to 2.
        backoff_factor (int or float, optional): The factor by which the delay is multiplied for each subsequent retry.
        Defaults to 2.

    Returns:
        function: A wrapper function that adds retry logic to the decorated function.

    Raises:
        Exception: An exception is raised if the function fails after the maximum number of retries.

    Example:
        @retry_with_exponential_backoff(max_retries=3, initial_delay=1, backoff_factor=2)
        def some_function():
            # function implementation

        # This will run `some_function`, retrying up to 3 times with delays of 1, 2, and 4 seconds.
    """

    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except InternalServerError as e:
                    print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds.")
                    print(e)
                    time.sleep(delay)
                    delay *= backoff_factor
                except GoogleAPICallError as e:
                    print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds.")
                    print(e)
                    time.sleep(delay)
                    delay *= backoff_factor
                except AttributeError as e:
                    print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds.")
                    print(e)
                    time.sleep(delay)
            raise ValueError(f"Function {func.__name__} failed after {max_retries} retries")

        return wrapper

    return decorator_retry


def concurrent_best_reduce(num_calls):
    """
    Decorator to run a function concurrently multiple times and return the best result.

    This decorator enhances a function by executing it concurrently across multiple threads, 
    using a ThreadPoolExecutor.
    The results from all concurrent executions are compared based on a specified metric (assumed to be the second 
    element of the return tuple),
    and the best result (highest score according to the metric) is returned.

    Args:
        num_calls: The number of times to concurrently execute the wrapped function.

    Returns:
        Callable: A decorated version of the input function that performs concurrent execution and returns the best 
        result.

    Example:
        @concurrent_best_reduce(num_calls=3)
        def my_func(arg1, arg2) -> Tuple[Any, float]:
            # ... do some work
            return result, score  # Where score is the metric to optimize

        best_result = my_func("input1", "input2")
    """

    def decorator(func: Callable[..., tuple[Any, float]]) -> Callable[..., tuple[Any, float]]:
        def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, float]:
            """
            Inner wrapper to handle concurrent execution and result selection.

            Args:
                *args: Positional arguments for the wrapped function.
                **kwargs: Keyword arguments for the wrapped function.

            Returns:
                Tuple[Any, float]: The best result from the concurrent executions (result, score).
            """
            results: list[tuple[Any, float, bool]] = []
            with ThreadPoolExecutor(max_workers=num_calls) as executor:
                futures = [executor.submit(func, *args, **kwargs) for _ in range(num_calls)]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result[2]:
                            results.append(result)
                    except TimeoutError:
                        print("A function call exceeded the timeout and was skipped.")
                    except Exception as e: # pylint: disable=W0718
                        print(f"A function call failed due to an error: {e}")

            if not results:
                print(f"All {num_calls} attempted calls were unsuccessful")
                return (
                    {
                        "answer": "I was not able to answer this question",
                        "plan_and_summaries": "",
                        "context_used": "[]",
                        "additional_information_to_retrieve": "",
                    },
                    0,
                    False
                )

            print(f"Selecting the best result from {len(results)} successful calls out of {num_calls} attempted...")
            best_result: tuple[Any, float, bool] = max(results, key=lambda x: x[1])
            return best_result

        return wrapper

    return decorator


def timeout_llm_call(timeout):
    """
    Decorator that enforces a timeout on an LLM call.

    Args:
        timeout: The maximum time (in seconds) that the LLM call is allowed to run.

    Returns:
        A decorator function that can be applied to other functions to enforce the timeout.
    """

    def decorator_timeout(func: Callable[..., tuple[Any, float]]) -> Callable[..., tuple[Any, float]]:
        """
        Inner decorator function that applies the timeout to the wrapped function.

        Args:
            func: The function to be wrapped and have a timeout applied.

        Returns:
            The wrapped function with timeout enforcement.
        """
        def wrapper_timeout(*args: Any, **kwargs: Any) -> tuple[Any, float]:
            """
            Wrapper function that actually executes the wrapped function with timeout handling.

            Args:
                *args: Positional arguments to be passed to the wrapped function.
                **kwargs: Keyword arguments to be passed to the wrapped function.   


            Returns:
                A tuple containing the output of the wrapped function and the confidence score.
            """
            try:
                return func_timeout(timeout, func, args=args, kwargs=kwargs)
            except FunctionTimedOut:
                output = {}
                print("Crashed because of timeout")
                output["answer"] = "I was not able to answer this question"
                output["plan_and_summaries"] = ""
                output["context_used"] = "[]"
                output["additional_information_to_retrieve"] = ""
                return output, 0, False

        return wrapper_timeout

    return decorator_timeout


class LLMExponentialRetryWrapper:
    """
    A wrapper class for LLMChain that adds exponential retry logic to the `run` method.

    This class wraps an instance of LLMChain and overrides its `run` method to include
    retry logic with exponential backoff. All other methods and attributes of the LLMChain
    are accessible and behave as they are in the original LLMChain class.

    Attributes:
        chain (LLMChain): The LLMChain instance that is being wrapped.

    Methods:
        run(*args, **kwargs): Executes the `run` method of the LLMChain with retry logic.
        __getattr__(name): Delegates attribute access to the LLMChain instance.
    """

    def __init__(self, chain):
        """
        Initializes the LLMExponentialRetryWrapper with an LLMChain instance.

        Args:
            chain (LLMChain): The LLMChain instance to wrap.
        """
        self.chain = chain
        self._run_with_retry = self._create_run_with_retry()

    def _create_run_with_retry(self):
        """
        Creates a wrapped version of the `run` method with exponential retry logic.

        The retry logic is applied via the `retry_with_exponential_backoff` decorator.

        Returns:
            function: A function that wraps the `run` method of LLMChain with retry logic.
        """

        @retry_with_exponential_backoff()
        def run_with_retry(*args, **kwargs):
            return self.chain.run(*args, **kwargs)

        return run_with_retry

    def run(self, *args, **kwargs):
        """
        Executes the `run` method of the LLMChain with retry logic.

        This method applies exponential backoff retry logic to the `run` method of the
        LLMChain. It accepts any combination of arguments that the original `run` method accepts.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The return value of the `run` method from LLMChain.
        """
        return self._run_with_retry(*args, **kwargs)

    def __getattr__(self, name):
        """
        Delegates attribute access to the LLMChain instance.

        This method is called if there isn't an attribute with the given name
        on the LLMExponentialRetryWrapper instance. It allows access to all methods
        and attributes of the LLMChain instance as if they were part of this wrapper class.

        Args:
            name (str): The name of the attribute being accessed.

        Returns:
            The attribute from the LLMChain instance.
        """
        return getattr(self.chain, name)
