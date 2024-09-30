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

import logging

import requests
import streamlit as st
from get_backend_url import get_backend_url

st.set_page_config(page_title="Prepare Data")


@st.cache_resource
def get_cached_backend_url():
    return get_backend_url()


backend_api_url = get_cached_backend_url()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info(f"Backend API URL: {backend_api_url}")


def next_step():
    st.session_state.current_step += 1


def prev_step():
    st.session_state.current_step -= 1


if "current_step" not in st.session_state:
    st.session_state.current_step = 0

if "index_name" not in st.session_state:
    st.session_state["index_name"] = "default"

if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0


def next_step():
    st.session_state["current_step"] += 1


def prev_step():
    st.session_state["current_step"] -= 1


def configure_input():
    st.subheader("📥 Input Configuration")
    input_type = st.selectbox("Select Input Type", ["url", "gcs"], key="input_type")

    if input_type == "url":
        url = st.text_input("Enter URL to be indexed", key="input_url")
        if st.button("Save URL Configuration", key="save_url_config"):
            st.session_state.input_config = {"type": "url", "config": {"url": url}}
            st.success("URL configuration saved!")
    elif input_type == "gcs":
        with st.expander("GCS Configuration"):
            project_name = st.text_input("GCP Project ID", key="gcs_project_name")
            bucket_name = st.text_input("GCS Bucket Name", key="gcs_bucket_name")
            prefix = st.text_input("GCS Prefix (optional)", key="gcs_prefix")
        if st.button("Save GCS Configuration", key="save_gcs_config"):
            st.session_state.input_config = {
                "type": "gcs",
                "config": {
                    "project_name": project_name,
                    "bucket_name": bucket_name,
                    "prefix": prefix,
                },
            }
            st.success("GCS configuration saved!")


def configure_data_loader():
    st.subheader("🔄 Data Loader Configuration")
    loader_type = st.selectbox(
        "Select Data Loader Type", ["document_ai"], key="data_loader_type"
    )

    if loader_type == "document_ai":
        with st.expander("Document AI Configuration"):
            project_id = st.text_input("Project ID", key="doc_ai_project_id")
            location = st.text_input("Location", key="doc_ai_location")
            processor_name = st.text_input(
                "Processor Name",
                key="doc_ai_processor_name",
                help=(
                    "Must be of format"
                    " projects/PROJECT_ID/locations/LOCATION/processors/PROCESSOR_ID"
                ),
            )
            gcs_output_path = st.text_input(
                "GCS Output Path", key="doc_ai_gcs_output_path"
            )
        if st.button("Save Document AI Configuration", key="save_doc_ai_config"):
            st.session_state.data_loader_config = {
                "type": "document_ai",
                "config": {
                    "project_id": project_id,
                    "location": location,
                    "processor_name": processor_name,
                    "gcs_output_path": gcs_output_path,
                },
            }
            st.success("Document AI configuration saved!")


def configure_document_splitter():
    st.subheader("✂️ Document Splitter Configuration")
    splitter_type = st.selectbox(
        "Select Document Splitter Type",
        ["recursive_character"],
        key="splitter_type",
    )

    with st.expander("Splitter Configuration"):
        chunk_size = st.number_input(
            "Chunk Size", value=1000, key="splitter_chunk_size"
        )
        chunk_overlap = st.number_input(
            "Chunk Overlap", value=100, key="splitter_chunk_overlap"
        )
    if st.button("Save Splitter Configuration", key="save_splitter_config"):
        st.session_state.document_splitter_config = {
            "type": splitter_type,
            "config": {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap},
        }
        st.success(f"{splitter_type.capitalize()} splitter configuration saved!")


def configure_vector_store():
    st.subheader("🗄️ Vector Store Configuration")
    store_type = st.selectbox(
        "Select Vector Store Type",
        ["vertex_ai", "generic"],
        key="vector_store_type",
    )

    if store_type == "vertex_ai":
        with st.expander("Vertex AI Configuration"):
            project_id = st.text_input("Project ID", key="vertex_ai_project_id")
            region = st.text_input("Region", key="vertex_ai_region")
            index_id = st.text_input("Index ID", key="vertex_ai_index_id")
            endpoint_id = st.text_input("Endpoint ID", key="vertex_ai_endpoint_id")
            embedding_model = st.selectbox(
                "Embedding Model",
                [
                    "text-embedding-004",
                    "text-embedding-preview-0815",
                    "text-multilingual-embedding-002",
                ],
                key="vertex_ai_embedding_model",
            )
            index_name = st.text_input("Index Name", key="vertex_ai_index_name")
        if st.button("Save Vertex AI Configuration", key="save_vertex_ai_config"):
            st.session_state.vector_store_config = {
                "type": "vertex_ai",
                "config": {
                    "project_id": project_id,
                    "region": region,
                    "index_id": index_id,
                    "endpoint_id": endpoint_id,
                    "embedding_model": embedding_model,
                    "index_name": index_name,
                },
            }
            st.success("Vertex AI configuration saved!")

    # elif store_type == "generic":
    #     index_name = st.text_input("Index Name", key="generic_index_name")
    #     if st.button("Save Generic Vector Store Configuration", key="save_generic_config"):
    #         st.session_state.vector_store_config = {
    #             "type": "generic",
    #             "config": {"index_name": index_name},
    #         }
    #         st.success("Generic vector store configuration saved!")


def review_and_index():
    st.subheader("📊 Review Configuration and Index Data")
    st.json(
        {
            "input_config": st.session_state.get("input_config", {}),
            "data_loader_config": st.session_state.get("data_loader_config", {}),
            "document_splitter_config": st.session_state.get(
                "document_splitter_config", {}
            ),
            "vector_store_config": st.session_state.get("vector_store_config", {}),
        }
    )

    if st.button("Index Data", type="primary", key="index_data_button"):
        if all(
            key in st.session_state
            for key in [
                "input_config",
                "data_loader_config",
                "document_splitter_config",
                "vector_store_config",
            ]
        ):
            request_data = {
                "input": st.session_state.input_config,
                "data_loader": st.session_state.data_loader_config,
                "document_splitter": st.session_state.document_splitter_config,
                "vector_store": st.session_state.vector_store_config,
            }
            with st.spinner("Indexing data..."):
                response = requests.post(
                    url=f"{backend_api_url}/index/trigger-indexing-job",
                    json=request_data,
                )
                if response.status_code == 200:
                    st.success(f"Indexing job started: {response.json()}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        else:
            st.error("Please configure all components before indexing.")

    # if st.button("Delete Index", type="primary", key="delete_index_button"):
    #     if "vector_store_config" in st.session_state:
    #         index_name_to_delete = st.session_state.vector_store_config["config"]["index_name"]
    #         with st.spinner(f"Deleting index: {index_name_to_delete}"):
    #             response = requests.post(
    #                 url=f"{backend_api_url}/delete-index-collection",
    #                 json={"index_name": index_name_to_delete},
    #             )
    #             if response.status_code == 200:
    #                 st.success(f"Index deleted: {response.json()}")
    #                 st.session_state.pop("vector_store_config", None)
    #             else:
    #                 st.error(f"Error: {response.status_code} - {response.text}")
    #     else:
    #         st.error("No index configuration found. Please configure the vector store first.")


def app():
    st.title("🚀 Prepare Data")
    st.write("Configure your data processing pipeline")

    steps = [
        ("Input Configuration", configure_input),
        ("Data Loader Configuration", configure_data_loader),
        ("Document Splitter Configuration", configure_document_splitter),
        ("Vector Store Configuration", configure_vector_store),
        ("Review and Index", review_and_index),
    ]

    n_steps = len(steps)

    # Main container for the current step
    container = st.empty()

    # Navigation buttons
    cols = st.columns(2)
    with cols[0]:
        st.button(
            "⬅️ Previous",
            on_click=prev_step,
            use_container_width=True,
            disabled=(st.session_state.current_step == 0),
        )
    with cols[1]:
        st.button(
            "Next ➡️",
            on_click=next_step,
            use_container_width=True,
            disabled=(st.session_state.current_step == n_steps - 1),
        )

    # Fill layout
    with container.container():
        current_step = st.session_state.current_step % n_steps
        # st.subheader(steps[current_step][0])
        steps[current_step][1]()

    # Progress bar
    st.progress((st.session_state.current_step + 1) / n_steps)


if __name__ == "__main__":
    app()
