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
"""Module for file and directory operations, including interaction with Google Cloud Storage.

**Key Functions:**

* **create_directory(directory)**: Creates a directory structure with specified 
permissions (0o777).
* **copy_from_gcs(gcs_bucket, destination_folder)**: Copies data from a GCS bucket to a local 
directory using the `gsutil` tool.
* **copy_resources()**:  Coordinates the process of loading configuration, preparing local 
directories, and transferring resources from a GCS bucket.
"""

import os
import shutil
import subprocess

import click
from gen_ai.common import common


LLM_YAML_FILE = "gen_ai/llm.yaml"

def create_directory(directory: str):
    """Creates a directory with specified permissions.

    This function attempts to create the directory and all necessary parent
    directories. If the directory already exists, no action is taken. It then
    sets the permissions of the directory to 0o777 (read, write, execute for all users).

    Args:
        directory (str): The path of the directory to be created.

    Raises:
        OSError: If an error occurs during directory creation or permission setting.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        os.chmod(directory, 0o777)
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")


def copy_from_gcs(gcs_bucket: str, destination_folder: str):
    """Copies files and directories from a Google Cloud Storage bucket to a destination folder.

    This function utilizes the 'gsutil' command-line tool to perform the data transfer.

    Args:
        gcs_bucket (str): The name of the GCS bucket to copy from.
        destination_folder (str): The local directory path where files will be copied.

    Raises:
        subprocess.CalledProcessError: If the 'gsutil' command fails with a non-zero exit code.
    """
    gsutil_command = f"gsutil -m cp -r {gcs_bucket}/* {destination_folder}"
    try:
        result = subprocess.run(
            gsutil_command, shell=True, check=True, capture_output=True
        )
        print(result.stdout.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print(f"gsutil copy failed: {e.stderr.decode('utf-8')}")

@click.command()
@click.argument("gcs_source_bucket", required=False)
def copy_resources(gcs_source_bucket: str | None = None):
    """Copies resources from a Google Cloud Storage (GCS) bucket to a local directory.

    This function performs the following steps:

    1. **Loads configuration:** Retrieves the GCS bucket name from a YAML configuration file.
    2. **Defines base path:** Sets the base directory for storing resources.
    3. **Determines company-specific directory:** Creates a subdirectory for a specified company.
    4. **Handles existing directories:** If the company directory already exists, it is removed 
    to ensure fresh resources are copied.
    5. **Creates necessary directories:** Creates the full path for resource storage, including any intermediate directories.
    6. **Copies resources from GCS:** Calls the `copy_from_gcs` function to transfer resources from 
    the GCS bucket to the local directory.
    """

    config = common.load_yaml(LLM_YAML_FILE)
    base_path = "/mnt/resources"
    gcs_bucket = gcs_source_bucket or config["gcs_source_bucket"]
    dataset_name = config["dataset_name"]

    if not os.path.exists(base_path):
        create_directory(base_path)
    company_directory = os.path.join(base_path, dataset_name)
    if os.path.exists(company_directory):
        try:
            shutil.rmtree(company_directory)
        except OSError as e:
            print(f"Error removing old directory {company_directory}: {e}")
    full_path = os.path.join(company_directory, "main_folder")
    os.makedirs(full_path, exist_ok=True)

    copy_from_gcs(gcs_bucket, full_path)


if __name__ == "__main__":
    copy_resources()
