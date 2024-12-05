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


import streamlit as st
import yaml 
import os
import streamlit as st
import Agents

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Agents.OrchestratorAgent(model="gemini-1.5-pro-001")
    st.session_state.orchestrator.start_conversation()
    st.session_state.messages = []  # Initialize chat history

orchestrator = st.session_state.orchestrator


###_____________PAGE CONFIG_____________###
st.set_page_config(
    page_title="Agentic Supply Chain Maintenance",
    layout="wide",
    initial_sidebar_state="expanded",
)



###_____________SIDEBAR_____________###

st.sidebar.title('Agentic SCM')

st.sidebar.header('', divider='blue')
st.sidebar.markdown('Leverage Agents to support with Maintenance and Logistics processes.')
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")


# /locations/global/engines/agenticscm_1724844048143/data/documents?e=13802955&mods=-autopush_coliseum&project=msubasioglu-genai-sa
# projects/742157128610/locations/global/collections/default_collection/engines/aircraft-manuals-scm_1724843980774 

st.sidebar.header('', divider='blue')


uploaded_file = st.sidebar.file_uploader("",type=(["jpg", "jpeg", "png", "svg", "webp"]))
 
if st.sidebar.button("Analyze Image"):
    if not uploaded_file: 
        st.sidebar.write("Please upload an image first.")

    else: 
        st.chat_message("assistant").write("Thanks for uploading an image. Please wait a moment while I analyze it for you.")  # Display directly
        # To read file as bytes:
        image = uploaded_file.getvalue()
        original_filename = uploaded_file.name
        filename = os.path.join(os.getcwd(), original_filename)
        filename = os.path.basename(filename)

        with open(filename, "wb") as f:
            f.write(image)

        response, response_list = orchestrator.send_message(filename)
        out_dict = {
            "trace": response_list, 
            "response": response
        }
        # st.session_state.messages.append({"role": "assistant", "content": out_dict})  # Add only the agent's response
        # st.chat_message("assistant").json(out_dict) 
        st.chat_message("assistant").write(out_dict['response'])

        # Expander for the trace
        with st.expander("Show Trace"):
            st.json(out_dict['trace'])  



###_____________MAIN PAGE_____________### 



# st.title('SCM Agents')


# st.text("")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# for msg in st.session_state.messages:
#     # st.chat_message(msg["role"],avatar="🤖").write(msg["content"])
#     st.chat_message(msg["role"]).write(msg["content"])




if prompt := st.chat_input():

    # st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response, response_list = orchestrator.send_message(prompt)
    out_dict = {
        "trace": response_list, 
        "response": response
    }
    # st.session_state.messages.append({"role": "assistant", "content": out_dict})
    # st.chat_message("assistant").json(out_dict)  
    st.chat_message("assistant").write(out_dict['response'])

    # Expander for the trace
    with st.expander("Show Trace"):
        st.json(out_dict['trace'])    



st.text("")


# VISIBILITY CONFIG 
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False













