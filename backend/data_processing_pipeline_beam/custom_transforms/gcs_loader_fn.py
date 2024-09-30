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
from custom_transforms.docai_parser import DocAIParser


class GCSLoaderFn(beam.DoFn):

  def setup(self):
    """DoFn for loading and processing GCS documents."""
    self.parsers = {}

  def process(self, element):
    """Process a GCS document element.

    Args:
        element (dict): The input element containing GCS blob and configuration.

    Yields:
        tuple: A tuple containing the document source and the processed
        document.
    """
    try:
      base_element = element["base_element"]
      data_loader_config = base_element["data_loader"]["config"]
      document_splitter_config = base_element["document_splitter"]["config"]
      vector_store_config = base_element["vector_store"]["config"]

      parser_key = (
          data_loader_config["project_id"],
          data_loader_config["location"],
          data_loader_config["processor_name"],
      )
      if parser_key not in self.parsers:
        self.parsers[parser_key] = DocAIParser(
            project_id=data_loader_config["project_id"],
            location=data_loader_config["location"],
            processor_name=data_loader_config["processor_name"],
            gcs_output_path=data_loader_config["gcs_output_path"],
        )

      parser = self.parsers[parser_key]
      blob = element["blob"]
      chunk_size = document_splitter_config["chunk_size"]
      index_name = vector_store_config["index_name"]

      docs = list(
          parser.online_process(
              blob,
              chunk_size=chunk_size,
              include_ancestor_headings=True,
          )
      )
      logging.info(f"Loaded {len(docs)} documents from GCS")

      for doc in docs:
        doc.metadata["index_name"] = index_name
        doc.metadata["input_type"] = "gcs"
        doc.metadata["base_element"] = base_element
        source = doc.metadata.get("source", f"gcs_{blob}")
        yield (source, doc)

    except Exception as e:
      logging.error(f"Error processing GCS document: {str(e)}")
