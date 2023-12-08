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

project_id          = "jk-mlops-dev"
region              = "us-central2"
prefix              = "jk1"
deletion_protection = true
cpu_node_pools = {
  default-cpu-node-pool = {
    zones = ["us-central2-a"]
  }
}
tpu_node_pools = {
  tpu-v4-16-node-pool = {
    zones          = ["us-central2-b"]
    min_node_count = 1
    max_node_count = 1
    tpu_type       = "v4-16"
  }
}
tensorboard_config = {
  region = "us-central1"
}
