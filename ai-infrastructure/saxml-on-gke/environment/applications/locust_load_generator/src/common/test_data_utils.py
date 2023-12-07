# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jsonlines
import re

from typing import List
from google.cloud import storage


def load_test_prompts(gcs_path: str) -> List[str]:
    gcs_uri_pattern = "^gs:\/\/[a-z0-9.\-_]{3,63}\/(.+\/)*(.+)$"
    if not re.match(gcs_uri_pattern, gcs_path):
        raise ValueError(f"Incorrect GCS URI: {gcs_path}")

    client = storage.Client()
    bucket_name = gcs_path.split('/')[2]
    blob_name = "/".join(
        gcs_path.split('/')[3:])
    bucket = client.get_bucket(bucket_name)
    blob = storage.Blob(blob_name, bucket)
    data_file_name = '/tmp/data.jsonl'
    with open(data_file_name, 'wb') as f:
        blob.download_to_file(f)
    test_data = []
    with jsonlines.open(data_file_name) as reader:
        for obj in reader:
            test_data.append(obj['input'])

    return test_data
