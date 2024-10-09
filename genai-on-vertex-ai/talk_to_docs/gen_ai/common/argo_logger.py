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
This module provides utilities for decorating functions to add logging and timing functionalities,
and for creating snapshots of logging data related to AI model processes. The provided functionalities
are designed to assist in monitoring and analyzing the performance of tasks by logging execution details
and measuring execution times.

The module integrates with a `Container` from a dependency injection framework, which manages application
configurations and provides system-wide utilities such as logging.

Functions:
    trace_on(msg: str, measure_time: bool = False): Decorates a function to log its execution details and,
        optionally, measure its execution time. It leverages the `Container`'s configuration to determine
        if system metrics should be logged.

    create_log_snapshot(react_snapshot: dict, retrieved_docs, post_filtered_docs,
        additional_information_to_retrieve, time_taken): Creates a detailed snapshot of logging data for AI
        processes, including pre and post filtered document information, additional info, and timing details.

Examples:
    Using the `trace_on` decorator to add logging to a function and optionally measure its execution time.
    Creating log snapshots after AI processing to capture and log state and performance data.

Dependencies:
    gen_ai.common.ioc_container: Provides the `Container` for accessing application configurations and logging.
    gen_ai.common.memorystore_utils: Utilities for converting data formats that support the logging process.
"""

import copy
from typing import Any

from gen_ai.common.document_utils import convert_langchain_to_json


def create_log_snapshot(
    react_snapshot: dict, retrieved_docs, post_filtered_docs, additional_information_to_retrieve, time_taken
) -> dict[str, Any]:
    """
    Creates a comprehensive logging snapshot that encapsulates information about a reaction process
    within an AI model's execution, including both pre and post document filtering stages.

    This function consolidates various pieces of information into a structured snapshot, which is useful
    for debugging, monitoring, and analyzing the behavior and performance of AI models during processing.

    Args:
        react_snapshot (dict): The initial snapshot data to be augmented with additional details.
        retrieved_docs (list[Document]): The list of documents retrieved before any filtering.
        post_filtered_docs (list[Document]): The list of documents after applying post-retrieval filtering.
        additional_information_to_retrieve (str): Any additional information specified for retrieval that
            complements the main processing.
        time_taken (float): The total time taken for the process, typically measured to evaluate performance.

    Returns:
        dict[str, Any]: A deep copy of the initial react snapshot augmented with details about retrieved
        and post-filtered documents, additional informational content, and the time taken for the process.

    Raises:
        TypeError: If the inputs do not conform to the expected types, particularly if `react_snapshot` is
        not a dictionary or the document lists are not list[Document].

    Example:
        >>> initial_snapshot = {'stage': 'initial'}
        >>> docs_pre_filter = [Document(...), Document(...)]
        >>> docs_post_filter = [Document(...)]
        >>> additional_info = "Extra data points"
        >>> time_spent = 0.234
        >>> log_snapshot = create_log_snapshot(
        ...     initial_snapshot,
        ...     docs_pre_filter,
        ...     docs_post_filter,
        ...     additional_info,
        ...     time_spent
        ... )
        >>> print(log_snapshot['time_taken'])
        0.234
    """
    log_shapshot = copy.deepcopy(react_snapshot)
    log_shapshot["pre_filtered_docs"] = [convert_langchain_to_json(x) for x in retrieved_docs]
    log_shapshot["post_filtered_docs"] = [convert_langchain_to_json(x) for x in post_filtered_docs]
    log_shapshot["additional_information_to_retrieve"] = additional_information_to_retrieve
    log_shapshot["time_taken"] = time_taken
    return log_shapshot
