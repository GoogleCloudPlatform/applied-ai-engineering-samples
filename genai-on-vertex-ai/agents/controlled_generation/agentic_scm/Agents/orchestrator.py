# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.   
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed    under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import json
import os
import sys
from vertexai.generative_models import GenerativeModel

from Tools import return_agent_instruction

# Add the path to your Agents module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import Agents  

def get_available_agents(model):
    """Dynamically discovers and returns a dictionary of available agents."""
    agents = {}
    for name, obj in inspect.getmembers(Agents):
        if inspect.isfunction(obj) and name.startswith("get_"):
            agent_name = name.replace("get_", "")
            try:
                # Assuming all agent functions take 'model' as an argument
                agent = obj(GenerativeModel(model))
                agents[agent_name] = agent
            except Exception as e:
                print(f"Error creating agent {agent_name}: {e}")
    return agents

class OrchestratorAgent(Agents.Agent):
    """
    An orchestrator agent that manages and calls other agents using an LLM.
    """

    def __init__(self, model):
        """
        Initializes the OrchestratorAgent with an LLM model and available agents.
        """
        # Generate tools string dynamically
        agents = get_available_agents(model)
        tools_string = "\nAvailable Agents:\n"
        for agent_name, agent_instance in agents.items():
            tools_string += f"- {agent_name}: {agent_instance.instructions}\n"

        super().__init__(
            model=GenerativeModel(model),
            response_schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "understanding": {
                            "type": "string",
                        },
                        "chain_of_thought": {
                            "type": "string",
                        },
                        "response": {
                            "type": "string",
                        },
                        "target_agent": {
                            "type": "string",
                        }, 
                        "agent_prompt": {
                            "type": "string",
                        }, 
                        "execute_agent": {
                            "type": "string",
                            "enum": [
                                "True",
                                "False"
                            ],
                        }, 
                    },
                    "required": ["understanding", "chain_of_thought", "response", "target_agent", "agent_prompt", "execute_agent"],
                },
            },

            persona="""I am an orchestrator agent. I can call other agents 
                       to perform different tasks if needed.""",
            instructions="""Analyze the user's message and determine which agent can best fulfill the request. 
                           Call the appropriate agent and return its response. Summarize what the agent did back to the user in your response. 
                           Do not execute the same agent twice. If the first execution did not return the expected result, return "Something went wrong" to the user.
                           If no agent should be called, set the execute_function parameter to False.
                           Make sure to provide the previous agents' response indicated to you by <SYSTEM_MESSAGE> back to the user to answer the initial query.""",
            tools=tools_string,
        )
        self.agents = agents


    def start_conversation(self):
        """
        Starts the conversation with the agent by sending the initial prompts.
        """
        guidelines = "<SYSTEM_MESSAGE> THIS IS A SYSTEM MESSAGE. BELOW IS YOUR DESCRIPTION FOR OPERATION. FOLLOW THESE INSTRUCTIONS AND AWAIT THE USER INPUT. YOU WILL BE PROVIDED WITH THE FULL CHAT HISTORY. MAKE SURE TO EMPHASIZE THE LATEST USER AND SYSTEM INPUTS MORE. </SYSTEM_MESSAGE> "
        persona_prompt = "<PERSONA>" + self.persona + "</PERSONA>"
        instruction_prompt = "<INSTRUCTIONS>" + self.instructions + "</INSTRUCTIONS>"
        tool_prompt = return_agent_instruction(self.tools)

        response = self.chat_session.send_message(
            guidelines + persona_prompt + instruction_prompt + tool_prompt
        )
        return response.text

    def send_message(self, message):
        """
        Sends a message to the agent and processes the response, potentially
        executing a tool function if instructed by the agent.
        """
        max_loop = 2 
        i = 0 

        response_list = list() 
        response = self.chat_session.send_message(f"<USER_INPUT> {message} </USER_INPUT> ")
        data = json.loads(response.text)
        response_list.append(data)

        idx = (len(data))-1
        execute_agent = data[idx]['execute_agent']
        target_agent = data[idx]['target_agent']
        agent_prompt = data[idx]['agent_prompt']
        user_response = data[idx]['response']

        while execute_agent == "True" and i < max_loop:
            print("\n--------Internal response:-------- \n", str(data[idx]))
            print("\n--------Now executing agent: ", target_agent, "--------\n")

            if target_agent:
            # Retrieve the target agent
                # try: 
                target_agent = self.agents.get(target_agent)
                if target_agent:
                    # Call the target agent's start_conversation and send_message method
                    response = target_agent.start_conversation()
                    response, subagents_list = target_agent.send_message(agent_prompt)
                    response_list.append(subagents_list)

                # except Exception as e: 
                #     return str(data[idx]), response_list

            response = self.chat_session.send_message(
                f"Here is the full response from the agent execution: <SYSTEM_INPUT>{str(response)}</SYSTEM_INPUT>"
            )
            
            try: 
                data = json.loads(response.text)
                response_list.append(data)

                idx = (len(data))-1
                execute_agent = data[idx]['execute_agent']
                target_agent = data[idx]['target_agent']
            
            except: return str(data[idx]['response']), response_list
            
            i+=1 

        return str(data[idx]['response']), response_list

