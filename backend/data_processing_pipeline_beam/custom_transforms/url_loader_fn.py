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
from langchain_community.document_loaders import WebBaseLoader


class URLLoaderFn(beam.DoFn):
  """DoFn for loading and processing URL documents."""

  def process(self, element):
    """Process a URL document element.

    Args:
        element (dict): The input element containing URL and configuration.

    Yields:
        tuple: A tuple containing the document source and the processed
        document.
    """
    try:
      url = element["url"]

      loader = WebBaseLoader(url)
      docs = loader.load()
      logging.info(f"Loaded {len(docs)} documents from URL: {url}")

      for doc in docs:
        doc.metadata["input_type"] = "url"
        doc.metadata["base_element"] = element["base_element"]
        source = doc.metadata.get("source", url)
        yield (source, doc)

    except Exception as e:
      logging.error(f"Error processing URL document: {str(e)}")
