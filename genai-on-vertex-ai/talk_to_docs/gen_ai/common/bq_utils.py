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
This module provides tools for interacting with Google BigQuery, including functions for creating clients,
datasets, and tables, as well as loading data. It leverages Google Cloud BigQuery to manage large-scale data
and analytics. The module contains utility functions to facilitate the creation and management of BigQuery
resources such as datasets and tables, and it provides a method to directly load data from a pandas DataFrame
into BigQuery, handling schema and client initialization. Additionally, it includes a specialized class
for converting structured data related to query states into a format suitable for analytics in BigQuery.

Classes:
    BigQueryConverter - Converts query state data into a pandas DataFrame for upload to BigQuery.

Functions:
    create_bq_client(project_id)
    create_dataset(client, dataset_id, location, recreate_dataset)
    create_table(client, table_id, schema, recreate_table)
    load_data_to_bq(client, table_id, schema, df)

Exceptions:
    GoogleAPIError - Handles API errors that may occur during interaction with Google services.
"""

import datetime
import getpass
import json
import os
import re
import uuid
from typing import Any

import git
import google.auth
import pandas as pd
from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import bigquery
from google.cloud.bigquery.schema import SchemaField

from gen_ai.common.document_utils import convert_dict_to_relevancies, convert_dict_to_summaries
from gen_ai.common.ioc_container import Container
from gen_ai.deploy.model import Conversation, QueryState
from gen_ai import __version__


def create_dataset(
    client: bigquery.Client, dataset_id: str, location: str = "US", recreate_dataset: bool = False
) -> None:
    """Creates a BigQuery dataset.
    If the dataset already exists, it will be deleted and recreated if recreate_dataset is True.
    Otherwise, an error will be raised.
    Args:
        client (bigquery.Client): The BigQuery client.
        dataset_id (str): The ID of the dataset to create.
        location (str, optional): The location of the dataset. Defaults to "US".
        recreate_dataset (bool, optional): Whether to recreate the dataset if it already exists. Defaults to False.
    """
    if recreate_dataset:
        client.delete_dataset(dataset_id, delete_contents=True, not_found_ok=True)
        print(f"Dataset {dataset_id} and its contents have been deleted.")
    try:
        client.get_dataset(dataset_id)
        print(f"Dataset {client.project}.{dataset_id} already exists")
    except NotFound:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = location
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {client.project}.{dataset.dataset_id}")


def create_table(
    client: bigquery.Client, table_id: str, schema: list[SchemaField], recreate_table: bool = False
) -> None:
    """Creates a BigQuery table.
    If the table already exists, it will be deleted and recreated if recreate_table is True.
    Otherwise, an error will be raised.
    Args:
        client (bigquery.Client): The BigQuery client.
        table_id (str): The ID of the table to create.
        schema (List[bigquery.SchemaField]): The schema of the table.
        recreate_table (bool, optional): Whether to recreate the table if it already exists. Defaults to False.
    """
    if recreate_table:
        try:
            client.get_table(table_id)
            client.delete_table(table_id)
            print(f"Table {table_id} deleted.")
        except NotFound:
            print(f"Table {table_id} does not exist. Skipping deletion.")

    table = bigquery.Table(table_id, schema=schema)
    try:
        client.get_table(table_id)
        print(f"Table {table_id} already exists.")
    except NotFound:
        table = client.create_table(table)
        print(f"Table {table_id} created.")


def load_data_to_bq(conversation: Conversation, log_snapshots: list[dict[str, Any]]):
    """Loads prediction data, question and exeriments information to BigQuery.

    This function prepares and loads relevant data from a conversation into BigQuery.
    The process involves extracting the latest question from the conversation,
    logging it for reference, and transforming the data into a format
    suitable for BigQuery using the `BigQueryConverter`.

    Args:
        conversation: A Conversation object containing the full conversation history.
        log_snapshots: A list of log snapshot objects containing relevant metadata.
    """
    query_state = conversation.exchanges[-1]
    question = query_state.question
    log_question(question)
    df = BigQueryConverter.convert_query_state_to_prediction(
        conversation.exchanges[-1], log_snapshots, conversation.session_id
    )
    load_status = load_prediction_data_to_bq(df)
    if load_status:
        Container.logger().info(msg="Successfully wrote into BQ Prediction table")
    else:
        Container.logger().info(msg="Error in writing into BQ Prediction table")


def load_prediction_data_to_bq(df: pd.DataFrame) -> None:
    """Loads data from a pandas DataFrame to a BigQuery table.
    The table will be created if it does not already exist.
    If the table already exists, it will be overwritten.
    Args:
        df (pandas.DataFrame): The DataFrame to load data from.
    """
    client = Container.logging_bq_client()
    dataset_id = get_dataset_id()

    table_id = f"{dataset_id}.prediction"
    table = client.get_table(table_id)
    schema = table.schema

    job_config = bigquery.LoadJobConfig(schema=schema)
    job = None
    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        print(f"Loaded {job.output_rows} rows into {table_id}.")

    except GoogleAPIError as e:
        Container.logger().error(msg="Crashed on writing into BQ Prediction table")
        Container.logger().error(msg=str(e))
        if job and job.errors:
            for error in job.errors:
                print(f"Error: {error['message']}")
                if "location" in error:
                    print(f"Field that caused the error: {error['location']}")
        return False
    return True


def log_system_status(session_id: str) -> str:
    """
    Logs the current system status and pipeline parameters to a BigQuery table for tracking and reproducibility.

    This function gathers essential information about the current execution context, including Git commit hash,
    GCS bucket location, model configuration, and optional user comments.
    It then generates a unique system state ID and inserts this data into an 'experiment' BigQuery table.

    Args:
        session_id (str): A unique identifier for the current user session.

    Returns:
        str: The generated system state ID.
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        git_hash = str(repo.head.object.hexsha)
    except git.exc.InvalidGitRepositoryError:
        print("Error: git repo not found.")
        git_hash = str(uuid.uuid5(uuid.NAMESPACE_DNS, os.getcwd()))

    gcs_bucket = Container.config["gcs_source_bucket"]
    model_name = Container.config["model_name"]
    temperature = Container.config["temperature"]
    max_output_tokens = Container.config.get("max_output_tokens", 4000)
    pipeline_parameters = f"model: {model_name}; temperature: {temperature}; max_tokens: {max_output_tokens}"

    comments = Container.comments
    system_state_id = str(
        uuid.uuid5(uuid.NAMESPACE_DNS, f"{git_hash}-{gcs_bucket}-{pipeline_parameters}-{comments or ''}")
    )

    data = {
        "system_state_id": system_state_id,
        "session_id": session_id,
        "github_hash": git_hash,
        "gcs_bucket_path": gcs_bucket,
        "pipeline_parameters": pipeline_parameters,
        "comments": comments,
    }
    data = {str(x): str(v) for x, v in data.items()}
    insert_status = insert_data_to_table("experiment", data)
    if not insert_status:
        print(f"Error while logging system state id to bq table. Github hash: {git_hash}; GCS bucket: {gcs_bucket}")
    Container.system_state_id = system_state_id
    return system_state_id


def log_question(question: str) -> str:
    """
    Logs a question into a BigQuery table and generates a unique question ID.

    This function does the following:

    * **Cleans the Question:** Removes non-alphanumeric characters from the question for ID generation.
    * **Generates Unique ID:** Creates a question ID using a UUID and the cleaned question text, ensuring uniqueness.
    * **Prepares Data:**  Formats the question and generated ID into a data structure for insertion.
    * **Inserts into BigQuery:** Inserts the formatted data into a 'questions' BigQuery table.
    * **Handles Errors:** Logs an error message if the BigQuery insertion fails.

    Args:
        question: The raw text of the question.

    Returns:
        str: The unique question ID.
    """
    question_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, re.sub(r"\W", "", question.lower())))
    data = {
        "question_id": question_id,
        "question": question,
        "parent_question_id": "",
    }

    insert_status = insert_data_to_table("questions", data)
    if not insert_status:
        print(f"Error while logging question {question} to bq table.")

    Container.question_id = question_id
    return question_id


def insert_data_to_table(table_name: str, data: dict[str, str]) -> bool:
    """
    Inserts a single row of data into a specified BigQuery table.

    This function assumes the data dictionary contains only string values.

    Args:
        table_name: The name of the target BigQuery table.
        data: A dictionary containing the data to be inserted, with keys as column names and values as strings.

    Returns:
        bool: True if the insertion was successful, False otherwise.
    """
    client = Container.logging_bq_client()
    dataset_id = get_dataset_id()
    table = client.get_table(f"{dataset_id}.{table_name}")

    errors = client.insert_rows_json(table, [data])
    if not errors:
        print("New rows have been added.")
        return True
    print(f"Errors while inserting rows: {errors}")
    return False


def get_dataset_id() -> str:
    """
    Retrieves the BigQuery dataset ID for the current project.

    The dataset ID combines the project ID and a predefined dataset name
    (assumed to be globally defined as 'DATASET_NAME').

    Priority for determining the project ID:

    1. **Variable in llm.yaml:** Looks for the 'bq_project_id' config variable.
    2. **Google Application Default Credentials:** If the environment variable is not found, uses Google's default
    credentials mechanism.

    Returns:
        str: The fully constructed BigQuery dataset ID in the format 'project_id.DATASET_NAME'.

    Raises:
        ValueError: If the project ID cannot be determined from either source.
    """
    project_id = Container.config.get("bq_project_id")
    dataset_name = Container.config["dataset_name"]
    if not project_id:
        _, project_id = google.auth.default()
    return f"{project_id}.{dataset_name}"


class BigQueryConverter:
    """
    A utility class for converting query state data into a pandas DataFrame that can be uploaded to BigQuery.

    This class is used to convert structured data from various stages of query processing, encapsulating it into
    a DataFrame. The DataFrame format is suitable for analytics and can be directly uploaded to BigQuery for
    further analysis. It handles the extraction of relevant fields from log snapshots associated with each
    query state, transforming them into a tabular form.

    Methods:
        convert_query_state_to_prediction(query_state, log_snapshots) - Converts log snapshots and a query state
                                                                        into a DataFrame structured for BigQuery.

    Usage:
        converter = BigQueryConverter()
        dataframe = converter.convert_query_state_to_prediction(query_state, log_snapshots)
    """

    @staticmethod
    def convert_query_state_to_prediction(
        query_state: QueryState, log_snapshots: list[dict], session_id: str
    ) -> pd.DataFrame:
        data = {
            "user_id": [],
            "prediction_id": [],
            "timestamp": [],
            "system_state_id": [],
            "session_id": [],
            "question_id": [],
            "question": [],
            "react_round_number": [],
            "response": [],
            "retrieved_documents_so_far": [],
            "post_filtered_documents_so_far": [],
            "retrieved_documents_so_far_content": [],
            "post_filtered_documents_so_far_content": [],
            "post_filtered_documents_so_far_all_metadata": [],
            "confidence_score": [],
            "response_type": [],
            "run_type": [],
            "time_taken_total": [],
            "time_taken_retrieval": [],
            "time_taken_llm": [],
            "tokens_used": [],
            "summaries": [],
            "relevance_score": [],
            "additional_question": [],
            "plan_and_summaries": [],
            "original_question": [],
            "app_version": []
        }
        max_round = len(log_snapshots) - 1
        system_state_id = Container.system_state_id or log_system_status(session_id)
        app_version = __version__
        for round_number, log_snapshot in enumerate(log_snapshots):
            react_round_number = round_number
            response = query_state.answer or ""
            retrieved_documents_so_far = json.dumps(
                [
                    {
                        "original_filepath": x["metadata"].get("original_filepath"),
                        "doc_identifier": x["metadata"].get("doc_identifier"),
                        "section_name": x["metadata"].get("section_name"),
                    }
                    for x in log_snapshot["pre_filtered_docs"]
                ]
            )
            post_filtered_documents_so_far = json.dumps(
                [
                    {
                        "original_filepath": x["metadata"].get("original_filepath"),
                        "doc_identifier": x["metadata"].get("doc_identifier"),
                        "section_name": x["metadata"].get("section_name"),
                    }
                    for x in log_snapshot["post_filtered_docs"]
                ]
            )
            retrieved_documents_so_far_content = json.dumps(
                [{"page_content": x["page_content"]} for x in log_snapshot["pre_filtered_docs"]]
            )
            post_filtered_documents_so_far_content = json.dumps(
                [{"page_content": x["page_content"]} for x in log_snapshot["post_filtered_docs"]]
            )
            post_filtered_documents_so_far_all_metadata = json.dumps([x for x in log_snapshot["post_filtered_docs"]])
            time_taken_total = query_state.time_taken
            time_taken_retrieval = 0
            time_taken_llm = 0
            response_type = "final" if react_round_number == max_round else "intermediate"

            tokens_used = query_state.tokens_used if query_state.tokens_used is not None else 0
            prediction_id = str(uuid.uuid4())

            timestamp = datetime.datetime.now()
            confidence_score = query_state.confidence_score
            summary = json.dumps([convert_dict_to_summaries(x) for x in log_snapshot["pre_filtered_docs"]])
            relevance_score = json.dumps([convert_dict_to_relevancies(x) for x in log_snapshot["pre_filtered_docs"]])
            additional_question = log_snapshot["additional_information_to_retrieve"]
            plan_and_summaries = str(log_snapshot["plan_and_summaries"])

            data["user_id"].append(getpass.getuser())
            data["prediction_id"].append(prediction_id)
            data["timestamp"].append(timestamp)
            data["system_state_id"].append(system_state_id)
            data["session_id"].append(session_id)
            data["question_id"].append(Container.question_id)
            data["question"].append(query_state.question)
            data["react_round_number"].append(str(react_round_number))
            data["response"].append(response)
            data["retrieved_documents_so_far"].append(retrieved_documents_so_far)
            data["post_filtered_documents_so_far"].append(post_filtered_documents_so_far)
            data["retrieved_documents_so_far_content"].append(retrieved_documents_so_far_content)
            data["post_filtered_documents_so_far_content"].append(post_filtered_documents_so_far_content)
            data["post_filtered_documents_so_far_all_metadata"].append(post_filtered_documents_so_far_all_metadata)
            data["confidence_score"].append(confidence_score)
            data["response_type"].append(response_type)
            data["run_type"].append("test")
            data["time_taken_total"].append(time_taken_total)
            data["time_taken_retrieval"].append(time_taken_retrieval)
            data["time_taken_llm"].append(time_taken_llm)
            data["tokens_used"].append(tokens_used)
            data["summaries"].append(summary)
            data["relevance_score"].append(relevance_score)
            data["additional_question"].append(additional_question)
            data["plan_and_summaries"].append(plan_and_summaries)
            data["original_question"].append(query_state.original_question)
            data["app_version"].append(app_version)

        df = pd.DataFrame(data)
        return df
