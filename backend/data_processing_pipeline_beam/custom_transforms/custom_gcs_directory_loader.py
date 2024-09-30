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
import re
from typing import List
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders.gcs_directory import GCSDirectoryLoader
from langchain_community.utilities.vertexai import get_client_info
from langchain_core.document_loaders.blob_loaders import Blob
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class CustomGCSDirectoryLoader(GCSDirectoryLoader, BaseLoader):

  def load(self, file_pattern=None) -> List[Document]:
    """Load documents."""
    try:
      from google.cloud import storage
    except ImportError:
      raise ImportError(
          "Could not import google-cloud-storage python package. "
          "Please install it with `pip install google-cloud-storage`."
      )
    client = storage.Client(
        project=self.project_name,
        client_info=get_client_info(module="google-cloud-storage"),
    )

    regex = None
    if file_pattern:
      regex = re.compile(r"{}".format(file_pattern))

    docs = []
    for blob in client.list_blobs(self.bucket, prefix=self.prefix):
      # we shall just skip directories since GCSFileLoader creates
      # intermediate directories on the fly
      if blob.name.endswith("/"):
        continue
      if regex and not regex.match(blob.name):
        continue
      # Use the try-except block here
      try:
        logger.info(f"Processing {blob.name}")
        temp_blob = Blob(path=f"gs://{blob.bucket.name}/{blob.name}")
        docs.append(temp_blob)
      except Exception as e:
        if self.continue_on_failure:
          logger.warning(f"Problem processing blob {blob.name}, message: {e}")
          continue
        else:
          raise e
    return docs
