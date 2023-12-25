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


output "cluster_name" {
  value = module.base_environment.cluster_name
}

output "region" {
  value = module.base_environment.region
}

output "artifact_registry_image_path" {
  value = module.base_environment.artifact_registry_image_path
}

output "namespace" {
  value = module.base_environment.workloads_namespace
}

output "gcs_buckets" {
  value = module.base_environment.gcs_buckets
}

output "ksa_name" {
  value = module.base_environment.wid_ksa
}
