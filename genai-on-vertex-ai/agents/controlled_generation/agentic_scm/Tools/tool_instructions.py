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


def return_tool_instruction(tools: str) -> str:
    TOOL_PROMPT = f""" 
                <TOOLS>
                "understanding": "This is what I understood the user wants from me",
                "chain_of_thought": "This is my chain of thought",
                "response": "This is the response I will provide back to the user",
                "function": "If I need to execute a function, this is the code to call it in the format 'function_name(arg1, arg2)'",
                "function_name": "This is the name of the function in the format 'function_name'", 
                "function_args": "These are the arguments of a function as a string.", 
                "execute_function": "Either 'True' or 'False', depending on whether I need to execute a function. 

                **EXAMPLE TOOL USAGE**: 
                "role": "model",
                "input": "<SYSTEM_MESSAGE> THIS IS A SYSTEM MESSAGE. BELOW IS YOUR DESCRIPTION FOR OPERATION. FOLLOW THESE INSTRUCTIONS AND AWAIT THE USER INPUT. YOU WILL BE PROVIDED WITH THE FULL CHAT HISTORY. MAKE SURE TO EMPHASIZE THE LATEST USER AND SYSTEM INPUTS MORE. </SYSTEM_MESSAGE>"
                "understanding": "This is a system message. I am awaiting further instructions.",
                "chain_of_thought": "I need to wait for the user input.",
                "response": "",
                "function": "",
                "function_name": "", 
                "function_args": "", 
                "execute_function": "False"  

                **EXAMPLE TOOL USAGE**: 
                "role": "user",
                "input": "<USER_INPUT> What is the sum of 3 and 8? </USER_INPUT>"
                "understanding": "The user is asking me about the sum of 3 and 8. I need to execute the function 'get_sum(3,8)'",
                "chain_of_thought": "To answer the user question, I first need to execute the function 'get_sum'. Then, when I get the function response back, I can formulate an answer back to the user.",
                "response": "",
                "function": "'get_sum(3, 8)'",
                "function_name": "'get_sum'", 
                "function_args": "3, 8", 
                "execute_function": "True"  

                **EXAMPLE TOOL USAGE**:
                "role": "model",  
                "input": "<SYSTEM_INPUT> 11 </SYSTEM_INPUT>" 
                "understanding": "The user asked me about the sum of 3 and 8. The function I called was executed and provided the result '11'",
                "chain_of_thought": "To answer the user question, I can use the result of the function execution",
                "response": "The sum of 3 and 8 is 11.",
                "function": "",
                "function_name": "", 
                "function_args": "", 
                "execute_function": "False"           

                You are provided the below tools to support you with your duties.  
                Do not hallucinate any data in your response. Only strictly stick to the information provided to you. 
                The tool will be executed by the application. The response of the tool execution will be provided back to you, indicated by the tag <SYSTEM_INPUT>. 

                Here is the list of tools available to you: 
                {tools}
                </TOOLS> 
                """
    return TOOL_PROMPT




def return_agent_instruction(agents: str) -> str:
    AGENTS_PROMPT = f""" 
                <AGENTS>
                "understanding": "This is what I understood I need to do",
                "chain_of_thought": "This is my chain of thought",
                "response": "This is the response I will provide back to the user",
                "target_agent": "If I need to call another agent, I will specify this here in the format 'TaskAgent'",
                "agent_prompt": "This is the message I need to forward to the agent.",
                "execute_agent": "Either 'True' or 'False', depending on whether I need to execute another agent. 

                **EXAMPLE TOOL USAGE**: 
                "role": "model",
                "input": "<SYSTEM_MESSAGE> THIS IS A SYSTEM MESSAGE. BELOW IS YOUR DESCRIPTION FOR OPERATION. FOLLOW THESE INSTRUCTIONS AND AWAIT THE USER INPUT. YOU WILL BE PROVIDED WITH THE FULL CHAT HISTORY. MAKE SURE TO EMPHASIZE THE LATEST USER AND SYSTEM INPUTS MORE. </SYSTEM_MESSAGE>"
                "understanding": "This is a system message. I am awaiting further instructions.",
                "chain_of_thought": "I need to wait for the user input.",
                "response": "",
                "target_agent": "",
                "agent_prompt": "",
                "execute_agent": "False".


                **EXAMPLE TOOL USAGE**: 
                "role": "user",
                "input": "<USER_INPUT> I need to analyze the following image: image/path.jpg </USER_INPUT>"
                "understanding": "The user wants to inspect an image. I should call the InspectorAgent.",
                "chain_of_thought": "To answer the user question, I first need to execute the agent 'InspectorAgent'. Then, when I get the agent response back, I can formulate an answer back to the user. If the returned response is a broken engine, I can ask the user if I should check for an available engine repair expert using the SchedulerAgent.",
                "response": "",
                "target_agent": "InspectorAgent",
                "agent_prompt": "Analyze this image: 'image/path.jpg'",
                "execute_agent": "True".

                **EXAMPLE TOOL USAGE**:
                "role": "model",  
                "input": "<SYSTEM_INPUT> The image shows a broken engine of a Boeing 747. </SYSTEM_INPUT>" 
                "understanding": "I called the InspectorAgent and it seems the image shows a broken engine of a Boeing 747. I should ask the user if I should check for an available Engine Repair Employee using the SchedulerAgent."
                "chain_of_thought": "To answer the user question, I can use the result of the agent execution",
                "response": "I analyzed the image using the InspectorAgent. It seems that it shows a broken engine of the Boeing 747. Do you want me to check for an available employee licensed for engine repairs?",
                "target_agent": "",
                "agent_prompt": "",
                "execute_agent": "False".          

                You are provided the below agents to support you with your duties.  
                Do not hallucinate any data in your response. Only strictly stick to the information provided to you. 
                The agents will be executed by the application. The response of the agents execution will be provided back to you, indicated by the tag <SYSTEM_INPUT>. 

                Here is the list of agents available to you: 
                {agents}
                </AGENST> 
                """
    return AGENTS_PROMPT