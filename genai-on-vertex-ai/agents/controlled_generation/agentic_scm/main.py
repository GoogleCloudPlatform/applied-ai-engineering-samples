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


import vertexai
import json 
import yaml 
import Agents 
from vertexai.generative_models import GenerativeModel

def load_config():
    """Loads configuration parameters from settings.yaml in the root directory."""
    config_file = "settings.yaml"
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

# Load the configuration
config = load_config()

# Access the project_id
project_id = config["project_id"]
location = config["location"]


vertexai.init(project=project_id, location=location)

# Create the orchestrator agent with the LLM model
orchestrator = Agents.OrchestratorAgent(model="gemini-1.5-pro-001")

# Example usage
print(orchestrator.start_conversation())

# response, response_list = orchestrator.send_message("I need to inspect an aircraft image: Files/TL-2000_StingSport.jpg")
# json_string = json.dumps(response_list, indent=4)
# print(response)

# response = orchestrator.send_message("Can you provide me with the maintenance documents?")
# print(response)

# response = orchestrator.send_message("I need an engine repair expert.")
response = orchestrator.send_message("I need to schedule for Engine Maintenance.")
print(response)



# # Get Agents 
InspectorAgent = Agents.get_InspectorAgent(model=GenerativeModel("gemini-1.5-pro-001"))
DocumentAgent = Agents.get_DocumentAgent(model=GenerativeModel("gemini-1.5-pro-001"))
SchedulerAgent = Agents.get_ScheduleAgent(model=GenerativeModel("gemini-1.5-pro-001"))
CustomsAgent = Agents.get_CustomsAgent(model=GenerativeModel("gemini-1.5-pro-001"))


# # ###### CUSTOMS AGENT ######
# # Start the conversation
# response = CustomsAgent.start_conversation()
# print("\n")
# print(response)
# print("\n")

# # Send a message to the agent
# response = CustomsAgent.send_message("I need to replace an airplane wing slat for the TL Sting Sport 2000")
# print(response)
# print("\n")



# ###### INSPECTOR AGENT ######
# # Start the conversation
# response = InspectorAgent.start_conversation()
# print("\n")
# print(response)
# print("\n")

# # Send a message to the agent
# response = InspectorAgent.send_message("Files/TL-2000 StingSport.webp")
# print(response)
# print("\n")



# ###### DOCUMENT AGENT ######
# # Start the conversation
# response = DocumentAgent.start_conversation()
# print("\n")
# print(response)
# print("\n")

# # Send a message to the agent
# response = DocumentAgent.send_message("What infos can you give me on the maintenance of TL-2000 StingSport?")
# print(response)
# print("\n")

# # Send a message to the agent
# response = DocumentAgent.send_message("Can you give me an overview of the annual safety reports?")
# print(response)
# print("\n")



# ###### SCHEDULER AGENT ######
# # Start the conversation
# response = SchedulerAgent.start_conversation()
# print("\n")
# print(response)
# print("\n")

# # Send a message to the agent
# response = SchedulerAgent.send_message("I need to schedule for Engine Maintenance.")
# print(response)
# print("\n")



