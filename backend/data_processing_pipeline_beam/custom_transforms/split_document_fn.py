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

import apache_beam as beam
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SplitDocumentFn(beam.DoFn):
  """DoFn for splitting documents."""

  def process(self, element):
    """Process and split a document element.

    Args:
        element (tuple): A tuple containing the document key and the document.

    Yields:
        tuple: A tuple containing the document key and the split document.
    """
    key, doc = element
    base_element = doc.metadata["base_element"]
    document_splitter_config = base_element["document_splitter"]["config"]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=document_splitter_config["chunk_size"],
        chunk_overlap=document_splitter_config["chunk_overlap"],
    )

    if doc.metadata.get("input_type") == "gcs":
      # GCS documents are already split by Document AI, so we return them as-is
      yield (key, doc)
    else:
      splits = splitter.split_documents([doc])
      for split in splits:
        split.metadata["base_element"] = base_element
        yield (key, split)
