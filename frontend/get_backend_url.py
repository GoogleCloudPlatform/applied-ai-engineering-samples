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

from google.auth import default
from google.cloud import run_v2


def get_backend_url():
  credentials, project = default()
  client = run_v2.ServicesClient(credentials=credentials)

  # Construct the full resource name of the Cloud Run service
  name = f"projects/{project}/locations/us-central1/services/backend-image"

  response = client.get_service(name=name)
  return response.uri


if __name__ == "__main__":
  print(get_backend_url())
