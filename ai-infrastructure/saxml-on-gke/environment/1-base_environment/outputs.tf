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

output "cluster_region" {
  value = var.region
}

output "wid_ksa_name" {
  value = var.wid_sa.ksa_name
}

output "wid_ksa_namespace" {
  value = var.wid_sa.ksa_namespace
}

output "wid_gsa_email" {
  value = module.wid_service_account.email
}

output "gcs_buckets" {
  value = module.base_environment.gcs_buckets
}

output "artifact_registry_image_path" {
  description = "The URI of an Artifact Registry if created"
  value       = try(module.base_environment.artifact_registry_image_path, null)
}
