# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st

st.set_page_config(
    page_title="RAG Playground",
    page_icon="🧠",
)

st.title("Welcome to RAG Playground! 🧠")

st.markdown("""
RAG Playground is a platform for experimenting with Retrieval Augmented Generation (RAG) techniques. 
It integrates with LangChain and Vertex AI, allowing you to compare different retrieval methods and LLMs on your own datasets.

## 🚀 Getting Started

1. **Prepare Your Data**: Start by ingesting and processing your data.
2. **Configure Experiments**: Set up different RAG configurations to compare.
3. **Run Queries**: Test your RAG setups with real queries.
4. **Evaluate Results**: Compare and analyze the generated answers.

## 📚 Key Features

- Flexible data ingestion from various sources
- Multiple retrieval methods (Top-K, Multi-Query, Contextual Compression)
- Integration with Vertex AI LLMs
- Automated and human-in-the-loop evaluations
- Intuitive UI for experimentation and visualization

## 🏁 Ready to begin?

Click the button below to start preparing your data:

""")

if st.button("🔢 Prepare Data", type="primary"):
  st.switch_page("pages/1_🔢_Prepare_Data.py")

st.sidebar.success("Select a page above.")
