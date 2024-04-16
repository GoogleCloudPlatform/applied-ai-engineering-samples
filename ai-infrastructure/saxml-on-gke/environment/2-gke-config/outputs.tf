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


locals {
  gke_settings = {
    namespace    = module.wid.namespace
    ksa_name     = module.wid.ksa_name
    wid_sa_name  = module.wid.wid_sa_name
    wid_sa_email = module.wid.wid_sa_email
  }
}

output "namespace" {
  description = "Saxml namespace"
  value       = var.namespace
}

output "ksa_name" {
  description = "Kubernetes wid service account"
  value       = var.ksa_name
}

output "iam_sa_email" {
  description = "IAM wid service account"
  value       = try(module.wid.created_resources.gsa_email, null)
}


resource "google_storage_bucket_object" "gke_settings" {
  for_each = var.automation.outputs_bucket == null ? {} : { 1 = 1 }
  name     = "${var.env_name}/settings/2-gke-setup-setting.json"
  bucket   = var.automation.outputs_bucket
  content  = jsonencode(local.gke_settings)
}
