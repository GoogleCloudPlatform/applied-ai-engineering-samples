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
"""Module for calculating and evaluating recall, scoring, and semantic similarity.

This module provides functions for calculating recall based on retrieved documents,
computing scores based on golden answers, and evaluating semantic similarity between
expected and retrieved text. It leverages various libraries and techniques, including
string matching, semantic embeddings, and data manipulation with pandas DataFrames.

The module is particularly useful for evaluating the performance of information
retrieval and question-answering systems, providing insights into how well the
system retrieves relevant information and generates accurate and semantically
meaningful responses.
"""

from ast import literal_eval
from collections import defaultdict

import click
import pandas as pd
from common.ioc_container import Container
from tqdm import tqdm

from gen_ai.common.eval_utils import golden_scoring_answer, substring_matching


def get_recall_from_paths(original_paths: list, expected_kc_docs: set) -> float:
    """Calculates recall based on the presence of expected documents in retrieved paths.

    This function iterates through a list of original document paths and checks if
    each path, after some preprocessing to extract the relevant document identifier,
    is present in a set of expected document identifiers. It returns the recall,
    which is the ratio of found documents to the total number of expected documents.

    Args:
        original_paths (list): A list of strings representing paths to retrieved documents.
        expected_kc_docs (set): A set of strings representing the expected document identifiers.

    Returns:
        float: The recall value, representing the proportion of expected documents found
               in the retrieved paths. A recall of 1 indicates that all expected documents
               were found.
    """
    if len(expected_kc_docs) == 0:
        return 1.0
    found_docs = set()
    for kc_doc in original_paths:
        if "-" in kc_doc:
            kc_doc = kc_doc.split("-")[1].strip()
        if "." in kc_doc:
            kc_doc = kc_doc.split(".")[0].strip()
        if kc_doc in expected_kc_docs:
            found_docs.add(kc_doc)
    return len(found_docs) / len(expected_kc_docs)


def get_expected_docs(row: pd.Series) -> dict:
    """Extracts and prepares expected document identifiers from a DataFrame row.

    This function processes a row of a DataFrame, typically containing ground truth
    information, to extract and structure expected document identifiers. It handles
    cases where the identifiers are stored as strings or lists, converting them into
    a consistent format.

    Args:
        row (pd.Series): A row from a pandas DataFrame, expected to contain columns
                         like 'gt_kmid' and 'set_number' representing document identifiers.

    Returns:
        dict: A dictionary containing lists of expected document identifiers, categorized
              by identifier type (e.g., 'kc', 'b360').
    """
    expected_docs = defaultdict(set)
    if str(row["gt_kmid"]) == "nan":
        expected_docs["kc"] = []
    else:
        print(row["gt_kmid"], type(row["gt_kmid"]))
        if isinstance(row["gt_kmid"], str):
            relevant_docs_kc_all = [row["gt_kmid"].lower()]
        else:
            relevant_docs_kc_all = literal_eval(row["gt_kmid"])
        relevant_docs_kc = [x.lower() for x in relevant_docs_kc_all]  # Using set comprehension to directly create a set
        relevant_docs_kc = [x for x in relevant_docs_kc if x != "km1708500"]  # exclude because Mahesh said
        expected_docs["kc"] = relevant_docs_kc

    expected_docs["b360"].add(row["set_number"].lower())
    expected_docs["b360"] = list(expected_docs["b360"])
    return expected_docs


def get_recall_in_post_filtered(row: pd.Series, expected_docs: dict) -> dict:
    """Calculates recall for different document types after post-filtering.

    This function computes recall scores for various document types (e.g., 'kc', 'b360')
    based on the retrieved documents and the expected documents. It compares the
    retrieved document identifiers with the expected ones, considering the document
    type, and returns a dictionary of recall scores.

    Args:
        row (pd.Series): A row from a pandas DataFrame, typically representing a single
                         query or data point, containing information about retrieved documents.
        expected_docs (dict): A dictionary containing lists of expected document identifiers
                              for different document types.

    Returns:
        dict: A dictionary where keys represent document types and values are the
              calculated recall scores for those types.
    """
    recalls = {"kc": 0, "b360": 0}
    if len(expected_docs["b360"]) == 0:
        recalls["b360"] = 1
    if row["set_number"].lower() in expected_docs["b360"]:
        recalls["b360"] = 1
    original_paths = row["post_filtered_documents_so_far"]
    print(original_paths)
    original_paths = [x[0].lower() for x in original_paths]
    recalls["kc"] = get_recall_from_paths(original_paths, expected_docs["kc"])
    return recalls


def prepare_recall_calculation(session_id: str, df_gt: pd.DataFrame, ragas: bool = True) -> pd.DataFrame:
    """Prepares and calculates recall metrics for a given session.

    This function retrieves prediction data from a BigQuery table, joins it with
    ground truth data, and calculates recall scores for different document types.
    It handles data formatting, merging, and recall calculation, outputting a
    DataFrame enriched with recall information.

    Args:
        session_id (str): The identifier of the session for which to calculate recall.
        df_gt (pd.DataFrame): A DataFrame containing ground truth data, including
                              expected document identifiers.
        ragas (bool, optional): Flag indicating whether to convert data to RAGAS format.
                                Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame containing both prediction and ground truth data,
                      augmented with calculated recall scores for different document types.
    """
    client = Container.logging_bq_client()

    dataset_name = Container.config["dataset_name"]
    table_name = "prediction"
    table_id = f"{client.project}.{dataset_name}.{table_name}"

    sql = f"""
    SELECT * FROM `{table_id}` where session_id like ('%{session_id}%') and response_type='final'
    """

    df_predictions = client.query(sql).to_dataframe()
    df_predictions["question_to_join_on"] = df_predictions["original_question"]
    df_gt["question_to_join_on"] = df_gt["question"]
    df_gt.rename(columns={"KMID": "gt_kmid"}, inplace=True)

    # Joining on the question field
    df_joined = df_predictions.merge(df_gt, on="question_to_join_on", how="inner")
    # Process columns for ragas format if necessary
    if ragas:
        df_joined["post_filtered_documents_so_far_content"] = df_joined["post_filtered_documents_so_far_content"].apply(
            lambda x: convert_to_ragas(x, "page_content")
        )
        df_joined["post_filtered_documents_so_far"] = df_joined["post_filtered_documents_so_far"].apply(
            lambda x: convert_to_ragas(x, "original_filepath")
        )
    recalls_in_post_filtered_360, recalls_in_post_filtered_kc = [], []
    for i, row in df_joined.iterrows():
        expected_docs = get_expected_docs(row)
        recall_in_filtered = get_recall_in_post_filtered(row, expected_docs)
        recalls_in_post_filtered_360.append(recall_in_filtered["b360"])
        recalls_in_post_filtered_kc.append(recall_in_filtered["kc"])

    df_joined["recall_b360"] = recalls_in_post_filtered_360
    df_joined["recall_kc"] = recalls_in_post_filtered_kc

    # Average recall
    average_recall_b360 = df_joined["recall_b360"].mean()
    average_recall_kc = df_joined["recall_kc"].mean()
    print(f"Average Recall B360: {average_recall_b360}")
    print(f"Average Recall KC: {average_recall_kc}")
    return df_joined


def prepare_scoring_calculation(df_joined: pd.DataFrame) -> pd.DataFrame:
    """Prepares and calculates golden answer scores for a DataFrame.

    This function iterates through a DataFrame, extracts relevant information for
    scoring, and calculates golden answer scores based on the expected and actual
    answers. It then adds the scores to the DataFrame and returns the updated DataFrame.

    Args:
        df_joined (pd.DataFrame): The input DataFrame containing information about expected
                                  and actual answers, typically obtained after joining
                                  predictions with ground truth data.

    Returns:
        pd.DataFrame: The updated DataFrame with an additional column 'golden_score'
                      containing the calculated golden answer scores for each row.
    """
    golden_scores = []
    for i, row in tqdm(df_joined.iterrows(), total=len(df_joined)):
        # print(row)
        expected_answer = row["UPDATED Golden Answer Expected from Knowledge Assist"]
        if str(expected_answer) == "nan":
            expected_answer = row["Golden Answer Expected from Knowledge Assist"]
        actual_answer = row["response"]
        question = row["question_x"]
        score = golden_scoring_answer(question, expected_answer, actual_answer)

        golden_scores.append(score)

    df_joined["golden_score"] = golden_scores
    mean_golden_score = df_joined["golden_score"].mean()
    mean_conf_score = df_joined["confidence_score"].mean()
    print(f"Average Golden Score: {mean_golden_score}")
    print(f"Average Confidence Score: {mean_conf_score}")
    return df_joined


def get_semantic_score(expected_text: str, retrieved_actual_text: list) -> float:
    """Calculates a semantic similarity score between expected and retrieved text.

    This function computes a semantic similarity score between the expected text and
    the retrieved actual text. It handles cases where the expected text is empty and
    uses a substring matching technique to assess the similarity.

    Args:
        expected_text (str): The expected text, typically from a ground truth source.
        retrieved_actual_text (list): A list of strings representing the retrieved actual text.

    Returns:
        float: The semantic similarity score, ranging from 0.0 to 100.0, indicating
               the degree of similarity between the expected and retrieved text.
    """
    if str(expected_text) == "nan":
        return 100.0

    if not expected_text or not retrieved_actual_text:
        return 0.0

    retrieved_actual_text = "\n".join([x[0] for x in retrieved_actual_text])

    # Calculate the fuzzy similarity score
    score = substring_matching(expected_text, retrieved_actual_text)
    return score


def prepare_semantic_score_calculation(df_joined: pd.DataFrame) -> pd.DataFrame:
    """Prepares and calculates semantic similarity scores for a DataFrame.

    This function iterates through a DataFrame, extracts expected and retrieved text
    from relevant columns, calculates semantic similarity scores using the
    `get_semantic_score` function, and adds these scores as new columns to the DataFrame.

    Args:
        df_joined (pd.DataFrame): The input DataFrame containing expected and retrieved
                                  text in specific columns, typically after joining
                                  predictions with ground truth data.

    Returns:
        pd.DataFrame: The updated DataFrame with two new columns: 'b360_semantic_scores'
                      and 'kc_semantic_scores', containing the calculated semantic
                      similarity scores for each row.
    """
    b360_scores, kc_scores = [], []
    for i, row in tqdm(df_joined.iterrows(), total=len(df_joined)):
        # print(row)
        expected_kc_text = row["Response from KC"]
        expected_b360_text = row["Response from B360"]
        retrieved_actual_text = row["post_filtered_documents_so_far_content"]
        kc_semantic_score = get_semantic_score(expected_kc_text, retrieved_actual_text)
        b360_semantic_score = get_semantic_score(expected_b360_text, retrieved_actual_text)
        b360_scores.append(b360_semantic_score)
        kc_scores.append(kc_semantic_score)

    df_joined["b360_semantic_scores"] = b360_scores
    df_joined["kc_semantic_scores"] = kc_scores
    mean_b360_score = df_joined["b360_semantic_scores"].mean()
    mean_kc_score = df_joined["kc_semantic_scores"].mean()
    print(f"Average B360 Semantic Score: {mean_b360_score}")
    print(f"Average KC Semantic Score: {mean_kc_score}")
    return df_joined


@click.command()
@click.option("--session_id", required=True, help="Session ID for the SQL database query.")
@click.option("--output_file", required=True, type=click.Path(), help="Path to the output CSV file.")
@click.option("--input_csv", required=True, type=click.Path(), help="Path to the input CSV file with ground truth.")
@click.option("--ragas", is_flag=True, help="Convert to ragas format if set to True.")
def query_and_process(session_id: str, output_file: str, input_csv: str, ragas: bool):
    """Queries data, calculates metrics, and saves the results to a CSV file.

    This function performs a series of operations to retrieve data, calculate recall,
    scoring, and semantic similarity metrics, and then saves the processed data to
    a specified CSV file.

    Args:
        session_id (str): The identifier for the session to query data for.
        output_file (str): The path to the output CSV file where the processed data
                           will be saved.
        input_csv (str): The path to the input CSV file containing ground truth data.
        ragas (bool): Flag whether to convert for ragas friendly format
    """
    df_gt = pd.read_csv(input_csv)
    df_joined = prepare_recall_calculation(session_id, df_gt, ragas)
    df_joined = prepare_scoring_calculation(df_joined)
    df_joined = prepare_semantic_score_calculation(df_joined)
    df_joined.to_csv(output_file, index=None)


def convert_to_ragas(input_text: str, column_name: str) -> list:
    """Converts the string to the ragas friendly format removing new line characters

    Args:
        input_text (str): The input text which has a lot of new line symbols, and is actually a list under the hood.
        column_name (str): The column name to use from the list.
    Returns:
        Cleaned up list of strings
    """
    actual_list = []
    x_str = literal_eval(input_text)
    for page_content in x_str:
        content = page_content[column_name]
        content = content.replace("\n", "")
        actual_list.append([content])
    return actual_list


if __name__ == "__main__":
    query_and_process()
