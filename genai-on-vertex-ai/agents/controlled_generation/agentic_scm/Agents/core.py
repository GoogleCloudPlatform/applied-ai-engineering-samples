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

import json

from .session_handler import start_chat  
from Tools import return_tool_instruction, run_function 

def create_agent(model, response_schema, persona, instructions, tools):
    """Creates and returns an Agent instance with the given parameters."""
    agent = Agent(model, response_schema, persona, instructions, tools)
    return agent


class Agent:
    """
    A core agent class for interacting with a Gemini model.

    Attributes:
        model: The Gemini GenerativeModel instance.
        response_schema: The schema for the expected JSON response.
        persona: The persona of the agent.
        instructions: The instructions for the agent.
        tools: A string describing the available tools.
        chat_session: The ChatSession instance for managing the conversation.
    """

    def __init__(self, model, response_schema, persona, instructions, tools):
        """
        Initializes a new Agent instance.
        """
        self.model = model
        self.response_schema = response_schema
        self.persona = persona
        self.instructions = instructions
        self.tools = tools
        self.chat_session = start_chat(self.model, self.response_schema)

    def start_conversation(self):
        """
        Starts the conversation with the agent by sending the initial prompts.
        """
        guidelines = "<SYSTEM_MESSAGE> THIS IS A SYSTEM MESSAGE. BELOW IS YOUR DESCRIPTION FOR OPERATION. FOLLOW THESE INSTRUCTIONS AND AWAIT THE USER INPUT. YOU WILL BE PROVIDED WITH THE FULL CHAT HISTORY. MAKE SURE TO EMPHASIZE THE LATEST USER AND SYSTEM INPUTS MORE. </SYSTEM_MESSAGE> "
        persona_prompt = "<PERSONA>" + self.persona + "</PERSONA>"
        instruction_prompt = "<INSTRUCTIONS>" + self.instructions + "</INSTRUCTIONS>"
        tool_prompt = return_tool_instruction(self.tools)

        response = self.chat_session.send_message(
            guidelines + persona_prompt + instruction_prompt + tool_prompt, role='user'
        )
        return response.text

    def send_message(self, message):
        """
        Sends a message to the agent and processes the response, potentially
        executing a tool function if instructed by the agent.
        """
        response_list = list() 
        response = self.chat_session.send_message(f"<USER_INPUT> {message} </USER_INPUT> ")
        data = json.loads(response.text)
        response_list.append(data)

        idx = (len(data))-1
        execute_function = data[idx]['execute_function']
        function = data[idx]['function']
        function_name = data[idx]['function_name']
        function_args = data[idx]['function_args']

        while execute_function == "True":
            print("\n--------Internal response:--------\n ", str(data[idx]))
            print("\n--------Now executing function:  ", function_name, "--------\n")
            function_response = run_function(function, function_name, function_args)
            print("\n--------Function Response:--------\n ",function_response)
            response = self.chat_session.send_message(
                f"Here is the response from your function execution: <SYSTEM_INPUT>{str(function_response)}</SYSTEM_INPUT>", role='user'
            )
            data = json.loads(response.text)
            response_list.append(data)

            idx = (len(data))-1
            execute_function = data[idx]['execute_function']
            function = data[idx]['function']
            function_name = data[idx]['function_name']
            function_args = data[idx]['function_args']

        return str(data[idx]), response_list
        # else:
        #     return response