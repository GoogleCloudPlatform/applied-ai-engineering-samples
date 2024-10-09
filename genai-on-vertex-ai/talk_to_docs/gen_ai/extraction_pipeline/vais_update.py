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
This module provides functions for updating a Datastore entity with data from a directory.

Key features:
- Merges metadata JSON files with their corresponding text content in a specified directory.
- Creates a BigQuery dataset and table if they don't already exist.
- Inserts all rows from a Pandas DataFrame into a specified BigQuery table.
- Imports data from a Pandas DataFrame to a Google Cloud Discovery Engine Datastore in batches.
- Provides utility functions for text processing, such as removing stars and replacing consecutive whitespace.
"""

import json5
import os
import re

import google.auth
import pandas as pd
import requests
from google.auth.transport.requests import Request
from google.cloud import bigquery


def update_the_data_store(input_dir: str, config: dict[str, str], data_store_id: str | None = None):
    """
    Updates a Datastore entity with data from files located in a directory.

    This function consolidates the data files from the specified input directory, creates a BigQuery table 
    if necessary, loads the consolidated data into the BigQuery table, and finally imports the data 
    into a Datastore entity.

    Args:
        input_dir: The directory containing data files to be processed.
        config: A dictionary containing configuration settings:
            - "project_id": (Optional) The Google Cloud Project ID. If not provided, defaults to the current project.
            - "dataset_id": The BigQuery dataset ID.
            - "table_name": The BigQuery table name.
            - "data_store_id": The ID of the Datastore entity to be updated.
        data_store_id: (Optional) The ID of the Datastore entity. If not provided or set to "datastore", 
            defaults to the value from the "config" dictionary.

    Returns:
        True if the Datastore entity was successfully updated, False otherwise.
    """
    project_id = config.get("project_id")
    dataset_id = config.get("dataset_id")
    table_name = config.get("table_name")
    location = config.get("datastore_location")

    if not data_store_id or data_store_id == "datastore":
        data_store_id = config.get("data_store_id")

    if not project_id:
        _, project_id = google.auth.default()

    # BigQuery Client
    client = bigquery.Client(project=project_id)

    # create dataset and table if not exists
    create_dataset_and_table(client, project_id, dataset_id, table_name)
    print(f"Created dataset and table: {dataset_id}.{table_name}")
    # create merged json file
    df = merge_json_files(input_dir)
    print(f"Created dataframe from {len(df)} files")

    # put the json file into bq
    table_id = f"{project_id}.{dataset_id}.{table_name}"
    inserted = insert_all_rows(df, client, table_id)
    if not inserted:
        return False
    print("Pushed into the BQ table")

    # fetch to data store
    updated_data_store = import_to_datastore_batched(
        project_id,
        location,
        data_store_id,
        df,
        batch_size=100
    )
    print("Done updating the datastore")
    if not updated_data_store:
        return False
    return True


def replace_consecutive_whitespace(text: str) -> str:
    """
    Replaces consecutive whitespace characters (including spaces, tabs, and newlines) within 
    the given text with a single space.

    Args:
        text: The input text string.

    Returns:
        The modified text string with consecutive whitespace replaced.
    """
    return re.sub(r"\s+", " ", text)


def remove_stars_and_consecutive_whitespaces(text: str) -> str:
    """
    Removes all star signs (*) from the given text and then replaces any consecutive whitespace
    characters with a single space.

    Args:
        text: The input text string.

    Returns:
        The modified text string with stars removed and consecutive whitespace replaced.
    """
    text_without_stars = re.sub(r"\*", " ", text)  # Remove stars
    return replace_consecutive_whitespace(text_without_stars)  # Replace


def merge_json_files(input_dir: str) -> pd.DataFrame:
    """
    Merges metadata JSON files with their corresponding text content in a specified directory.

    This function iterates through the files in the given directory. For each "_metadata.json" file, 
    it extracts relevant information like the original filepath, section name, and content from a 
    corresponding text file (if it exists). It processes this data, creates unique IDs, and organizes 
    everything into a Pandas DataFrame.

    Args:
        input_dir: The directory containing the JSON and text files to be processed.

    Returns:
        A DataFrame with two columns: "id" (unique identifier for each entry) and "JsonData" 
        (containing the combined JSON data and text content).
    """
    final_json = {}

    for filename in os.listdir(input_dir):
        if filename.endswith("_metadata.json"):
            metadata_filepath = os.path.join(input_dir, filename)
            with open(metadata_filepath, "r", encoding="utf-8") as f:
                data = json5.load(f)
            key = os.path.basename(data.pop("original_filepath"))
            key = os.path.splitext(key)[0]
            key += f"_{data['section_name']}"
            key = re.sub(r"[^\w-]+", "", key)
            if len(key) > 60:
                key = key[:30] + key[-30:]
            final_json[key] = data

            # Look for matching text file
            txt_filename = filename.replace("_metadata.json", ".txt")
            txt_filepath = os.path.join(input_dir, txt_filename)
            if not os.path.exists(txt_filepath):
                continue
            with open(txt_filepath, "r", encoding="utf-8") as txt_f:
                content = txt_f.read()
            content = remove_stars_and_consecutive_whitespaces(content)
            if content and not content.isspace():
                final_json[key]["content"] = content

    df = pd.DataFrame(final_json.items(), columns=["id", "JsonData"])
    return df


def create_dataset_and_table(client, project_id: str, dataset_id: str, table_name: str):
    """
    Creates a BigQuery dataset and table if they don't already exist.

    Args:
        client: A BigQuery client object.
        project_id: The ID of the Google Cloud project.
        dataset_id: The ID of the dataset to create or use.
        table_name: The name of the table to create within the dataset.
    """
    # Create the dataset if it doesn't exist
    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    client.create_dataset(dataset, exists_ok=True)

    # Table Schema
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField(
            "JsonData", 
            "STRING", 
            mode="NULLABLE")
    ]

    table_id = f"{project_id}.{dataset_id}.{table_name}"

    table_exists = False
    try:
        client.get_table(table_id)  # Will raise NotFound exception if table doesn't exist
        table_exists = True
    except Exception as _:  # pylint: disable=W0718
        pass

    # Create Table (if not exists)
    if not table_exists:
        table = bigquery.Table(table_id, schema=schema)
        table = client.create_table(table)
        print(f"Created table {table_id}")
    else:
        print(f"Table {table_id} already exists. Please append rows if needed.")


def insert_all_rows(df: pd.DataFrame, client, table_id: str):
    """
    Inserts all rows from a Pandas DataFrame into a specified BigQuery table.

    Args:
        df: The DataFrame containing the data to insert.
        client: The BigQuery client object.
        table_id: The ID of the BigQuery table to insert data into.

    Returns:
        True if all rows were successfully inserted, False otherwise.
    """
    rows_to_insert = [
        {"id": df["id"][i], "JsonData": str(df["JsonData"][i])}
        for i in range(len(df))
    ]

    table = client.get_table(table_id)
    errors = client.insert_rows(table, rows_to_insert, row_ids=[None]*len(rows_to_insert))

    if not errors:
        print("Inserted all files into BigQuery.")
        return True
    else:
        print(f"Encountered errors while inserting rows: {errors}")
        return False


def import_to_datastore_batched(project_id: str, location: str, data_store_id: str, df: pd.DataFrame, batch_size=100):
    """
    Imports data from a Pandas DataFrame to a Google Cloud Discovery Engine Datastore in batches.

    Args:
        project_id (str): The ID of the Google Cloud project.
        data_store_id (str): The ID of the Discovery Engine Datastore.
        df (pd.DataFrame): The DataFrame containing the data to be imported. It is assumed to have 
                           columns "id" and "JsonData".
        batch_size (int, optional): The number of documents to import in each batch. Defaults to 100.

    Returns:
        bool: True if the import was successful for all batches, False otherwise.
    """
    # Authenticate with Google Cloud
    credentials, _ = google.auth.default()
    credentials.refresh(Request())
    auth_token = credentials.token

    all_rows = [
        {"id": df["id"][i], "jsonData": str(df["JsonData"][i])}
        for i in range(len(df))
    ]

    # 2. Prepare and send documents in batches
    parent = f"projects/{project_id}/locations/{location}/collections/" \
             f"default_collection/dataStores/{data_store_id}/branches/0"
    if location == "global":
        url = f"https://discoveryengine.googleapis.com/v1/{parent}/documents:import"
    else:
        url = f"https://{location}-discoveryengine.googleapis.com/v1/{parent}/documents:import"

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    total_count = 0
    success_count = 0
    for i in range(0, len(all_rows), batch_size):
        documents = all_rows[i : i + batch_size]

        if not documents:
            print("No documents found in this batch.")  # This shouldn't happen if rows exist
            continue

        data = {
            "inlineSource": {
                "documents": documents  
            }
        }
        response = requests.post(url, headers=headers, json=data, timeout=3600)
        if response.status_code == 200:
            r = json5.loads(response.text)
            if "failureCount" in r["metadata"]:
                print(f"Errors in importing batch: {r['metadata']['failureCount']} / {len(documents)}")
                success_count -= int(r["metadata"]["failureCount"])
            else:
                print(f"Batch imported successfully! (Rows {i+1}-{i+len(documents)})")
            print(r)
            total_count += len(documents)
            success_count += len(documents)
        else:
            print(f"Error importing batch: {response.status_code}, {response.text}")
            return False
    print(f"Successfully imported {success_count} of {total_count} documents.")
    return True
