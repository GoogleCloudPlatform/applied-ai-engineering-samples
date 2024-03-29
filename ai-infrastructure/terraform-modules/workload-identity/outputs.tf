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

output "created_resources" {
  description = "IDs of the resources created, if any."
  value = merge(
    var.namespace_create ? {
      namespace_name = var.namespace
    } : {},
    var.kubernetes_service_account_create ? {
      ksa_name = var.ksa_name
    } : {},
    var.google_service_account_create ? {
      gsa_name  = module.workload-service-account.0.name
      gsa_email = module.workload-service-account.0.email
    } : {}
  )
}

output "wid_sa_email" {
  description = "Email of the workload service account."
  value       = local.wid_sa_email
}

output "wid_sa_name" {
  description = "Name of the workload service account."
  value       = local.wid_sa_name
}

output "namespace" {
  description = "Name of the namespace."
  value       = var.namespace
}

output "ksa_name" {
  description = "Name of the Kubernetes service account."
  value       = var.ksa_name
}



