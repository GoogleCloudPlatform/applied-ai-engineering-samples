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
"""This module provides tools for extracting data from supported document formats (.pdf, .docx, .xml, .json).

It includes functions to process configuration files, process documents within a
directory, and a main function for command-line usage.
"""
import argparse
from concurrent.futures import as_completed, ProcessPoolExecutor
from datetime import datetime, timezone, timedelta
import os
import re
import shutil
import subprocess
import tempfile
import time
from timeit import default_timer

from gen_ai.extraction_pipeline.document_extractors.document_processor import DocumentProcessor
from gen_ai.extraction_pipeline.vais_update import update_the_data_store
from google.cloud.storage import Client, transfer_manager
import yaml

CONFIG_FILEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yaml")
PROCESSABLE_FILETYPES = set([".pdf", ".docx", ".xml", ".json", ".html", ".att_ni_xml"])


def process_config_file(config_file: str = "config.yaml") -> dict[str, str]:
    """Reads a YAML configuration file and extracts all parameters.

    Args:
        config_file (str): Path to the YAML configuration file. Defaults to
            "config.yaml".

    Returns:
        dict: A dictionary containing the extracted parameters.
    """

    with open(config_file, "r", encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as exception:
            print("Error parsing YAML file:", exception)
    return {}


def split_bucket_and_directory(uri: str):
    """Splits a GS bucket URI (gs://bucket_name/directory/path) into the bucket name and directory path.

    Args:
        uri (str): The GS bucket URI.

    Returns:
        tuple: A tuple containing the bucket name (str) and directory path (str).
    """

    parts = uri.split("/", 3)
    if len(parts) < 3:
        raise ValueError(
            "Invalid GS URI format. Must contain bucket name and directory path"
        )

    bucket_name = parts[2]
    directory_path = parts[3] if len(parts) == 4 else ""
    return bucket_name, directory_path


def process_directory(
        input_dir: str, output_dir: str, config_file_parameters: dict[str, str]
) -> bool:
    """Processes all files within a specified input directory.

    This function iterates through each file in the input directory,
    creates a DocumentProcessor instance, and utilizes the instance's
    process() method to extract and save data from the file to the output
    directory.

    Args:
        input_dir (str): Path to the directory containing files to be processed.
        output_dir (str): Path to the directory where processed results will be
            stored.
        config_file_parameters (dict[str, str]): Configuration parameters.
    Returns:
       bool: True if the operation was successful, False otherwise.
    """
    success = 0
    failure = 0
    futures = {}
    start_time = default_timer()
    with ProcessPoolExecutor() as executor:
        for filename in os.listdir(input_dir):
            file_extension = os.path.splitext(filename)[-1]
            if file_extension in PROCESSABLE_FILETYPES:
                filepath = os.path.join(input_dir, filename)
                extractor = DocumentProcessor(filepath, config_file_parameters)
                futures[executor.submit(extractor, output_dir)] = filepath
                print(f"Added {filepath}")
            else:
                print(
                    f"Failed extraction on: {filename}\nNot implemented File Extension"
                    f" {file_extension}"
                )

        for future in as_completed(futures):
            if future.result():
                print(f"Successfully processed: {futures[future]}")
                success += 1
            else:
                print(f"Unsuccessful extraction from {futures[future]}")
                failure += 1

    print(f"Successfully processed {success} out of {success+failure} files.")
    print(f"Output directory: {output_dir}")
    print(f"Total Directory Processing Time: {default_timer()-start_time}")

    if success:
        return True
    return False


def process_gsbucket(
    input_dir: str,
    output_dir: str,
    config_file_parameters: dict[str, str],
    since_timestamp: datetime | None = None
) -> bool:
    """Processes all files within a specified cloud bucket.

    This function iterates through each file in the input bucket, stores them in
    local temporary directory. Then creates a DocumentProcessor instance, and
    utilizes the instance's
    process() method to extract and save data from the file to the output
    directory.

    Args:
        input_dir (str): Path to the directory containing files to be processed.
        output_dir (str): Path to the directory where processed results will be
            stored.
        config_file_parameters (dict[str, str]): Configuration parameters.
        since_timestamp (datetime | None): Timestamp from which to process files.
    Returns:
       bool: True if the operation was successful, False otherwise.
    """
    start_gsbucket = default_timer()
    source_bucket_name, directory = split_bucket_and_directory(input_dir)
    storage_client = Client()
    bucket = storage_client.get_bucket(source_bucket_name)

    if since_timestamp is None:
        since_timestamp = datetime.min.replace(tzinfo=timezone.utc)

    blob_names = []

    blobs = bucket.list_blobs(prefix=directory)
    for blob in blobs:
        if blob.time_created > since_timestamp:
            basename = os.path.basename(blob.name)
            blob_names.append(basename)

    with tempfile.TemporaryDirectory() as tmp_directory:
        directory = os.path.join(directory, "")
        results = transfer_manager.download_many_to_path(
            bucket, blob_names, destination_directory=tmp_directory, blob_name_prefix=directory, max_workers=8
        )
        print(f"Copying giles took: {default_timer() - start_gsbucket} sec")
        for name, result in zip(blob_names, results):
            if isinstance(result, Exception):
                print(f"Failed to download {name} due to exception: {result}")
            else:
                print(f"Downloaded {name} to.")

        processed = process_directory(tmp_directory, output_dir, config_file_parameters)
    print(f"Total Bucket Processing Time: {default_timer()-start_gsbucket} sec")
    if processed:
        return True
    return False


def process_continuously(
    input_dir: str,
    config_file_parameters: dict[str, str | int],
    output: str
):
    """
    Continuously processes new files from a Google Cloud Storage (GCS) bucket with specified intervals.

    This function repeatedly performs the following steps in a loop:

    1. Checks if enough time has passed since the last processing.
    2. If so, it calls the `process_gsbucket` function to extract data from the input GCS bucket, placing the output in 
    a temporary directory.
    3. Copies the extracted data from the temporary directory to the output GCS bucket using the `copy_files_to_bucket` 
    function OR updates a Datastore with the extracted data using the `update_the_data_store` function.
    4. Removes the temporary directory.

    Args:
        input_dir (str): The GCS bucket path containing the input files.
        config_file_parameters (dict[str, str]): A dictionary containing parameters for the `process_gsbucket` function.
        output (str): The GCS bucket path or data store id to store the extracted output.
    """
    last_time = datetime.min.replace(tzinfo=timezone.utc)
    parse_interval = config_file_parameters.get("bucket_parse_interval")
    while True:
        current_time = datetime.now(timezone.utc)
        if current_time - last_time > timedelta(seconds=parse_interval):
            print("Performing an extraction round")
            temp_output_dir = f"temporary_directory_{current_time}"
            os.makedirs(temp_output_dir)
            processed = process_gsbucket(input_dir, temp_output_dir, config_file_parameters, since_timestamp=last_time)

            if output.startswith("gs://") and processed:
                copied = copy_files_to_bucket(temp_output_dir, output)
                if copied:
                    print(f"Successfully copied extractions to gs bucket {output}")

            elif output.startswith("datastore") and processed:
                data_store_id = output.split(":")[-1]
                updated = update_the_data_store(temp_output_dir, config_file_parameters, data_store_id)
                if updated:
                    print(f"Successfully updated the data_store {output}")

            shutil.rmtree(temp_output_dir)
            print(f"Processed gs bucket at: {current_time}")

        last_time = current_time

        time.sleep(60)


def copy_files_to_bucket(output_dir: str, gs_bucket: str) -> bool:
    """Copies files from a local output directory to a designated Google Cloud Storage bucket.

    Args:
        output_dir (str): Path to the local directory containing files to be copied.
        gs_bucket (str): The Google Cloud Storage bucket name in the format 'gs://bucket_name'

    Returns:
       bool: True if the copy operation was successful, False otherwise.

    Raises:
        subprocess.CalledProcessError: If the 'gsutil' command fails to execute successfully.
    """
    if not re.match(r"^gs://[a-z0-9.-_]+", gs_bucket):
        print(f"Wrong format of gs bucket address: {gs_bucket}")
        return False
    now = datetime.now()
    output_directory = f"extractions{now.year}{now.month:02d}{now.day:02d}"

    if not gs_bucket.endswith("/"):
        gs_bucket += "/"
    command = ["gsutil", "-m", "cp", "-r", f"{output_dir}/*", f"{gs_bucket}{output_directory}/"]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error copying files to bucket: {e}")
        return False
    return True


def main():
    """Main function of the extraction pipeline."""
    parser = argparse.ArgumentParser(
        prog="DocumentsExtractor", description="Process files in directory"
    )
    parser.add_argument(
        "mode", choices=["batch", "continuous"], help="Processing mode: batch or continuous"
    )

    parser.add_argument(
        "-i", "--input", help="Input directory or gs bucket", required=True
    )
    parser.add_argument(
        "-o", 
        "--output", 
        help="Output directory, gs bucket or datastore (output_data, gs://t2x_bucket or datastore:t2x_datastore)",
        default="output_data"
    )
    args = parser.parse_args()

    config_file_parameters = process_config_file(CONFIG_FILEPATH)

    if args.mode == "batch":
        if args.output.startswith("gs://") or args.output.startswith("datastore"):
            output_dir = f"temporary_directory_{datetime.now(timezone.utc)}"
        else:
            output_dir = args.output

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directory '{output_dir}' created.")

        if args.input.startswith("gs://"):
            processed = process_gsbucket(args.input, output_dir, config_file_parameters)
        else:
            processed = process_directory(args.input, output_dir, config_file_parameters)

        if args.output.startswith("gs://") and processed:
            copied = copy_files_to_bucket(output_dir, args.output)
            if copied:
                print(f"Successfully copied extractions to gs bucket {args.output}")
            shutil.rmtree(output_dir)

        elif args.output.startswith("datastore"):
            data_store_id = args.output.split(":")[-1]
            update_status = update_the_data_store(output_dir, config_file_parameters, data_store_id)
            if update_status:
                print(f"Successfully uploaded extractions to data store {args.output}")
            shutil.rmtree(output_dir)

    elif args.mode == "continuous":
        if not args.input.startswith("gs://"):
            parser.error("Argument input should be gs_bucket for continuous mode.")
        process_continuously(args.input, config_file_parameters, args.output)

if __name__ == "__main__":
    main()
