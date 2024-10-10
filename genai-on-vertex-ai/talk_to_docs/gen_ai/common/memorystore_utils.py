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
A module for handling operations related to memory storage, particularly for managing query states and document 
conversions within a conversational AI context. 

This module provides functionality to convert documents between JSON and a custom `Document` format, 
generate unique keys for storing query states in Redis, save query states to Redis, and retrieve them based on 
personalized data. It is designed to work within the `gen_ai` project, utilizing the project's inversion of control 
container for Redis connections and custom data types like `PersonalizedData` and `QueryState`.
"""

import json
from dataclasses import asdict
from datetime import datetime
from typing import List

from gen_ai.common.ioc_container import Container
from gen_ai.deploy.model import PersonalizedData, QueryState

DEFAULT_SESSION_ID = "123456789"


def generate_query_state_key(personalized_data: dict[str, str], unique_identifier: str | None = None) -> str:
    """
    Generates a unique key for storing a query state in Redis.

    The key is constructed using the member id number from the personalized data, along with a
    unique identifier.

    Args:
        personalized_data (dict[str, str]): The personalized data containing the policy and set number.
        unique_identifier (str): A unique identifier for the query state, typically a timestamp.

    Returns:
        str: A string key uniquely identifying a query state for storage in Redis.
    """
    the_key = f"query_state:{personalized_data['member_id']}"
    if "session_id" in personalized_data and personalized_data["session_id"]:
        the_key = f"{the_key}:{personalized_data['session_id']}"
    else:
        the_key = f"{the_key}:{DEFAULT_SESSION_ID}"
    if unique_identifier:
        the_key = f"{the_key}:{unique_identifier}"
    return the_key


def save_query_state_to_redis(query_state: QueryState, personalized_data: dict[str, str]) -> None:
    """
    Saves a query state to Redis using a generated key.

    This function serializes the `QueryState` object to JSON, including converting any
    `Document` objects within `retrieved_docs` to their JSON representation. It then generates
    a unique key and saves the serialized data to Redis.

    Args:
        query_state (QueryState): The query state to save.
        personalized_data (dict[str, str]): The personalized data used to generate part of the key.

    Side Effects:
        Saves a serialized version of the query state to Redis under a generated key.
    """
    query_state_json = json.dumps(asdict(query_state))

    unique_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

    key = generate_query_state_key(personalized_data, unique_identifier)

    Container.redis_db().set(key, query_state_json)


def get_query_states_from_memorystore(personalized_info: PersonalizedData) -> List[QueryState]:
    """
    Retrieves a list of `QueryState` objects from Redis based on personalized info.

    This function searches Redis for keys matching the policy and set number in the personalized info,
    deserializes the stored JSON data into `QueryState` objects, and returns a list of these objects.

    Args:
        personalized_info (PersonalizedData): The personalized information used to search for matching query states.

    Returns:
        List[QueryState]: A list of `QueryState` objects retrieved from Redis.
    """
    pattern = generate_query_state_key(personalized_info) + ":*"

    keys = Container.redis_db().keys(pattern)
    matching_query_states = []
    for key in keys:
        query_state_json = Container.redis_db().get(key)

        if query_state_json:
            query_state_dict = json.loads(query_state_json)

            query_state_obj = QueryState(**query_state_dict)
            timestamp = key.split(":")[-1]
            matching_query_states.append((timestamp, query_state_obj))

    matching_query_states.sort(key=lambda x: x[0], reverse=True)
    sorted_query_states = [qs[1] for qs in matching_query_states]

    return sorted_query_states


def serialize_previous_conversation(query_states: list[QueryState]) -> str:
    """
    Serializes the content of a previous conversation from a query state into a formatted string.

    This function takes the state of a previous query and formats it into a readable string detailing
    the question, the answer, and any additional information that was specified to be retrieved. This can
    be used for logging, debugging, or displaying past interaction context in a user interface.

    Args:
        query_states (list[QueryState]): The list of query state objects containing details of the previous conversation
                                  including the question asked, the answer given, and any additional
                                  information that was required.

    Returns:
        str: A string that summarizes the previous conversation in a structured format.

    Example:
        >>> query_state = QueryState(question="What is the capital of France?", answer="Paris",
                                     additional_information_to_retrieve="Population details")
        >>> serialized_conversation = serialize_previous_conversation([query_state])
        >>> print(serialized_conversation)
        Previous question #1 was: What is the capital of France?
        Previous answer #1 was: Paris
        Previous additional information to retrieve #1: Population details
    """
    serialized_previous_conversation = []

    for i, query_state in enumerate(query_states):
        response = f"""
        Previous question #{i} was: {query_state.question}
        Previous answer #{i} was: {query_state.answer} 
        Previous additional information to retrieve #{i} was: {query_state.additional_information_to_retrieve}"""
        serialized_previous_conversation.append(response)
    return "\n".join(serialized_previous_conversation)
