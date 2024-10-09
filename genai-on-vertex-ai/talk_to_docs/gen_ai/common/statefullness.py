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
A module dedicated to handling the statefulness of conversations within a conversational AI system.

This module offers functionality for resolving session information from memory stores and enriching current 
conversations with data from previous interactions. It leverages utilities for interacting with Redis to store and 
retrieve query states, aiming to provide a seamless and coherent conversational experience across sessions. 
The module integrates closely with the project's inversion of control container for logging and data management.

Classes:
- SessionResolver: Responsible for retrieving past conversation states based on personalized information.
- RequestEnricher: Enriches the current conversation request with information from past conversations.

Functions:
- resolve_and_enrich: Resolves past conversations and enriches the current conversation with them.
- serialize_response: Serializes the current conversation state and saves it to Redis.
"""

from typing import Any

from gen_ai.common.ioc_container import Container
from gen_ai.common.memorystore_utils import get_query_states_from_memorystore, save_query_state_to_redis
from gen_ai.deploy.model import Conversation, PersonalizedData, QueryState


class SessionResolver:
    """
    Resolves past conversation sessions from a memory store using personalized information.

    Attributes:
        personalized_info: The personalized information used to identify and retrieve relevant past conversations.

    Methods:
        get_previous_conversations: Retrieves and converts past query states to a usable format.
    """

    def __init__(self, personalized_info: PersonalizedData):
        """
        Initializes the SessionResolver with personalized information.

        Args:
            personalized_info: The personalized information used for identifying relevant past conversations.
        """
        self.personalized_info = personalized_info

    def get_previous_conversations(self) -> Any:
        """
        Retrieves past conversation states from the memory store.

        Uses the personalized information to find and convert stored query states into conversation objects.

        Returns:
            A list of past conversation objects if any are found, otherwise None.
        """
        previous_sessions = get_query_states_from_memorystore(self.personalized_info)
        if previous_sessions:
            return previous_sessions
        return None


class RequestEnricher:
    """
    Enriches a current conversation request with data from previous conversations.

    Attributes:
        previous_conversations (list[QueryState]): A list of previous conversation states to be used for enrichment.
        conversation (Conversation): The current conversation to be enriched.

    Methods:
        get_enriched_conversation: Enriches the current conversation with previous ones.
    """

    def __init__(self, previous_conversations: list[QueryState], conversation: Conversation) -> None:
        """
        Initializes the RequestEnricher with previous conversations and the current conversation.

        Args:
            previous_conversations (list[QueryState]): The previous conversations to enrich the current one.
            conversation (Conversation): The current conversation to be enriched.
        """
        self.previous_conversations = previous_conversations
        self.conversation = conversation

    def get_enriched_conversation(self) -> Any:
        """
        Enriches the current conversation by inserting exchanges from previous conversations at the beginning.

        Also logs the process of enriching the request with each previous conversation's question and answer.

        Returns:
            The enriched Conversation object.
        """
        for previous_conversation in self.previous_conversations:
            self.conversation.exchanges.insert(0, previous_conversation)
            Container.logger().info(msg="Enriching Request with question and answer")
            Container.logger().info(msg=f"Question: {previous_conversation.question}")
            Container.logger().info(msg=f"Answer: {previous_conversation.answer}")
        return self.conversation


def resolve_and_enrich(conversation: Conversation) -> Conversation:
    """
    Resolves past conversations for a given conversation and enriches it with those past conversations.

    Args:
        conversation (Conversation): The current conversation to be resolved and enriched.

    Returns:
        The enriched Conversation object if past conversations are found, otherwise returns the original conversation.
    """
    resolver = SessionResolver(conversation.member_info)
    previous_conversations = resolver.get_previous_conversations()
    if previous_conversations is None:
        return conversation

    enricher = RequestEnricher(previous_conversations, conversation)
    return enricher.get_enriched_conversation()


def serialize_response(conversation: Conversation):
    """
    Serializes the current conversation's latest exchange and saves it to Redis.

    Args:
        conversation: The conversation object whose latest exchange will be serialized and saved.

    Side Effects:
        Saves the serialized conversation state to Redis for future retrieval.
    """
    save_query_state_to_redis(conversation.exchanges[-1], conversation.member_info)
