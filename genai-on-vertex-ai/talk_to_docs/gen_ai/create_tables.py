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
This module is designed to facilitate the creation of datasets and tables in Google BigQuery. It is tailored 
specifically for managing the storage of large-scale experiment and evaluation data, including predictions, 
evaluations, ground truth, questions, and experimental setups.

The module utilizes predefined schemas for different table types which include predictions, evaluations, 
ground truths, questions, and experimental configurations. These schemas define the structure and data 
types of the tables to ensure consistency and compatibility with the expected data.

Functionality includes:
- Creating a BigQuery client with the option to specify a Google Cloud project ID.
- Creating a new dataset or optionally recreating an existing dataset.
- Creating or recreating tables within the specified dataset according to the provided schemas.

The module is run as a script which accepts command-line arguments to specify the BigQuery project, dataset, 
and whether to recreate the dataset or tables. This allows for easy integration into automated workflows 
and batch processing environments.

Example usage:
    python create_tables.py 'dataset_name' --recreate_table
    This example command would create or recreate tables in the 'dataset_name' dataset.

Attributes:
    schema_gt (list): Schema for the ground truth table.
    schema_prediction (list): Schema for the prediction table.
    schema_eval (list): Schema for the evaluation table.
    schema_question (list): Schema for the question table.
    schema_experiment (list): Schema for the experiment configuration table.

Command-line Arguments:
    --project_id (str): Optional. Specifies the Google Cloud project ID. If not provided, the default project is used.
    dataset_name (str): Required. Specifies the BigQuery dataset name where tables will be created or updated.
    --recreate_dataset (bool): Optional flag to force recreation of the dataset.
    --recreate_table (bool): Optional flag to force recreation of tables within the dataset.

This module depends on the `google-cloud-bigquery` package for interacting with BigQuery and assumes 
that the appropriate Google Cloud credentials are available in the environment.
"""

import argparse

from google.cloud import bigquery

from gen_ai.common.bq_utils import create_dataset, create_table, get_dataset_id
from gen_ai.common.ioc_container import Container

schema_gt = [
    bigquery.SchemaField("question_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("question", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("gt_answer", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("gt_document_names", "STRING", mode="REPEATED"),
]

schema_prediction = [
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("prediction_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("system_state_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("question_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("question", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("react_round_number", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("response", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("retrieved_documents_so_far", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("post_filtered_documents_so_far", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("retrieved_documents_so_far_content", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("post_filtered_documents_so_far_content", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("post_filtered_documents_so_far_all_metadata", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("confidence_score", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("response_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("run_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("time_taken_total", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("time_taken_retrieval", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("time_taken_llm", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("tokens_used", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("summaries", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("relevance_score", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("additional_question", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("plan_and_summaries", "STRING", mode="REQUIRED"),
]

schema_eval = [
    bigquery.SchemaField("prediction_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("system_state_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("question_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("react_round_number", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("metric_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("metric_level", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("metric_value", "FLOAT64", mode="REQUIRED"),
    bigquery.SchemaField("metric_confidence", "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("metric_explanation", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("run_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("response_type", "STRING", mode="REQUIRED"),
]

schema_question = [
    bigquery.SchemaField("question_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("question", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_question_id", "STRING", mode="NULLABLE"),
]

schema_experiment = [
    bigquery.SchemaField("system_state_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("github_hash", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("gcs_bucket_path", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("pipeline_parameters", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("comments", "STRING", mode="NULLABLE"),
]

if __name__ == "__main__":
    # example usage: python create_tables.py 'dataset_name' --recreate_table
    parser = argparse.ArgumentParser(description="Create BigQuery tables.")
    parser.add_argument("--recreate_dataset", action="store_true", help="Flag to recreate the dataset")
    parser.add_argument("--recreate_table", action="store_true", help="Flag to recreate the tables")
    args = parser.parse_args()

    client = Container.logging_bq_client()
    dataset_id = get_dataset_id()

    create_dataset(client, dataset_id, recreate_dataset=args.recreate_dataset)

    schemas = [schema_prediction, schema_eval, schema_gt, schema_question, schema_experiment]
    tables_names = ["prediction", "query_evaluation", "ground_truth", "questions", "experiment"]

    for schema, table_name in zip(schemas, tables_names):
        table_id = f"{dataset_id}.{table_name}"
        create_table(client, table_id, schema, args.recreate_table)
