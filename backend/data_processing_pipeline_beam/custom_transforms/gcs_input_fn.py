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
import apache_beam as beam
from custom_transforms.custom_gcs_directory_loader import CustomGCSDirectoryLoader


class LogInputFn(beam.DoFn):
  """DoFn for logging input elements."""

  def process(self, element):
    """Log the received input element.

    Args:
        element: The input element to log.

    Yields:
        The input element unchanged.
    """
    logging.info(f"Received input: {element}")
    yield element


class GCSInputFn(beam.DoFn):
  """DoFn for processing GCS input elements."""

  def process(self, element):
    """Process a GCS input element.

    Args:
        element (dict): The input element containing GCS configuration.

    Yields:
        dict: A dictionary containing the processed GCS blob and base element.
    """
    try:
      input_config = element["input"]["config"]

      loader = CustomGCSDirectoryLoader(
          project_name=input_config["project_name"],
          bucket=input_config["bucket_name"],
          prefix=input_config["prefix"],
      )

      doc_blobs = loader.load()
      for blob in doc_blobs:
        yield {
            "type": "gcs",
            "blob": blob,
            "base_element": element,
        }

    except Exception as e:
      logging.error(f"Error processing input: {str(e)}")
