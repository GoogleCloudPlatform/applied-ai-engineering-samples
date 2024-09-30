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

import requests
import streamlit as st
from get_backend_url import get_backend_url
from google.cloud import firestore
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header

st.set_page_config(page_title="Query Data", layout="wide")
db = firestore.Client()


@st.cache_resource
def get_cached_backend_url():
    return get_backend_url()


backend_api_url = get_cached_backend_url()


def get_index_names():
    try:
        response = requests.get(f"{backend_api_url}/retrieval/index-names")
        response.raise_for_status()
        return response.json()["index_names"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching index names: {str(e)}")
        return []


def update_feedback(feedback_key):
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    st.session_state.feedback[feedback_key] = st.session_state[feedback_key]


def app():
    st.title("🧪 RAG Experiment Playground")
    st.markdown("Configure your query parameters and run experiments")
    add_vertical_space(2)

    colored_header(
        label="Query Configuration",
        description="Set up your experiment parameters",
        color_name="blue-70",
    )

    with st.form("query_form"):
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Queries and Index")
            rag_queries = st.text_area(
                "Retrieval Queries (one per line)",
                value=(
                    "What are the main challenges of deploying ML models?\nHow can we"
                    " overcome these challenges?"
                ),
                height=150,
            )
            st.info(
                "Enter one query per line. These queries will be used for retrieval"
                " and comparison."
            )

            index_names = get_index_names()
            selected_index = st.selectbox("Select Index", index_names)
            st.info("Choose the dataset index to use for RAG Experiments")

        with col2:
            st.subheader("Models and Techniques")
            retrievers = st.multiselect(
                "Select retrieval techniques",
                ["TopK", "MultiQueryRetriever", "ContextualCompressionRetriever"],
            )

            llms = st.multiselect(
                "Select LLMs",
                [
                    "gemini-1.0-pro-001",
                    "gemini-1.0-pro-002",
                    "gemini-1.5-pro-001",
                    "gemini-1.5-flash-001",
                ],
            )

        add_vertical_space(1)
        colored_header(
            label="Advanced Settings",
            description="Fine-tune your experiment",
            color_name="blue-30",
        )

        col3, col4, col5 = st.columns(3)

        with col3:
            temperature = st.slider("Temperature", 0.0, 2.0, 0.0, step=0.1)
            st.info(
                "Controls randomness in output. Higher values increase creativity,"
                " lower values increase determinism."
            )
            max_output_tokens = st.number_input("Max Output Tokens", 1, 8192, 8192)
            st.info("Maximum number of tokens in the generated response.")

        with col4:
            top_p = st.slider("Top P", 0.0, 1.0, 0.95, step=0.01)
            st.info(
                "Nucleus sampling: only consider tokens with cumulative probability <"
                " top_p."
            )
            top_k = st.number_input("Top K", 1, 40, 40)
            st.info("Only consider the top k tokens for each generation step.")

        with col5:
            is_rerank = st.checkbox("Use Reranker", value=False)
            st.info(
                "Enable to use a reranker on the retrieved documents before passing"
                " them to the LLM."
            )

        submit_button = st.form_submit_button(
            "🚀 Run Experiment", type="primary", use_container_width=True
        )

    if submit_button:
        queries = [q.strip() for q in rag_queries.split("\n") if q.strip()]
        retriever_model_pairs = [
            {"model_name": llm, "retriever_name": retriever}
            for llm in llms
            for retriever in retrievers
        ]
        model_params = {
            llm: {
                "model_name": llm,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "top_p": top_p,
                "top_k": top_k,
            }
            for llm in llms
        }

        with st.spinner("Running experiment..."):
            try:
                response = requests.post(
                    url=f"{backend_api_url}/retrieval/compare-retrieval-results",
                    json={
                        "queries": queries,
                        "retriever_model_pairs": retriever_model_pairs,
                        "model_params": model_params,
                        "index_name": selected_index,
                        "is_rerank": is_rerank,
                    },
                )
                response.raise_for_status()
                st.session_state.query_results = response.json()
                st.success("Experiment completed successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error running experiment: {str(e)}")

    if "query_results" in st.session_state:
        display_results(st.session_state.query_results)


def display_results(query_results):
    st.subheader("🔍 Experiment Results")
    results = query_results.get("results", [])

    if not results:
        st.warning("No results to display.")
    else:
        grouped_results = {}
        for result in results:
            query = result.get("query", "N/A")
            model = result.get("model_name", "N/A")
            retriever = result.get("retriever_name", "N/A")
            if query not in grouped_results:
                grouped_results[query] = {}
            if retriever not in grouped_results[query]:
                grouped_results[query][retriever] = {}
            grouped_results[query][retriever][model] = result

        for query_idx, (query, retrievers) in enumerate(grouped_results.items()):
            st.markdown(f"#### Query {query_idx + 1}: {query}")

            for retriever, models in retrievers.items():
                st.markdown(f"#### Retriever: {retriever}")

                cols = st.columns(len(models))
                for col, (model, result) in zip(cols, models.items()):
                    with col:
                        with st.expander(f"**Model: {model}**"):
                            st.markdown("**Answer:**")
                            st.markdown(f"{result.get('answer', 'N/A')}")
                            st.divider()
                            st.markdown("**Evaluation Metrics:**")
                            if "eval_result" in result:
                                metrics = result["eval_result"]
                                metric_data = {}

                                for metric_key, metric_value in metrics.items():
                                    if "/" in metric_key:
                                        metric, component = metric_key.split("/")
                                        if metric not in metric_data:
                                            metric_data[metric] = {}
                                        metric_data[metric][component] = metric_value

                                for metric, components in metric_data.items():
                                    st.markdown(
                                        f"**{metric.replace('_', ' ').title()}**"
                                    )
                                    if "score" in components:
                                        st.metric("Score", f"{components['score']:.2f}")
                                    if "explanation" in components:
                                        st.markdown(
                                            f"**Explanation:** {components['explanation']}"
                                        )
                                    st.divider()

                            feedback_key = f"feedback_{query_idx}_{model}_{retriever}"
                            st.markdown("**Your Feedback:**")
                            feedback = st.feedback(
                                options="stars",
                                key=feedback_key,
                                on_change=update_feedback,
                                args=(feedback_key,),
                            )

                st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Feedback", use_container_width=True):
            if "feedback" in st.session_state and st.session_state.feedback:
                st.success("Feedback saved successfully!")
                st.json(st.session_state.feedback)
            else:
                st.warning("No feedback to save.")

    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            for key in ["query_results", "feedback"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    app()
