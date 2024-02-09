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
  automation_bucket_name = module.automation_gcs.name
  automation_sa_name     = var.automation_sa_name
  automation_sa_email    = "${var.automation_sa_name}@${var.project_id}.iam.gserviceaccount.com"

  _tpl_providers = "${path.module}/templates/providers.tf.tpl"
  _tpl_backend   = "${path.module}/templates/backend.tf.tpl"

  providers = {
    "providers" = templatefile(local._tpl_providers, {
      sa = module.automation_sa.email
    })

    "backend" = templatefile(local._tpl_backend, {
      backend_extra = join("\n", [
        "# Set the prefix to the folder for Terraform state",
        "prefix = \"<FOLDER-NAME>\""
      ])
      bucket = module.automation_gcs.name
      sa     = module.automation_sa.email
    })
  }

  tfvars = {
    automation = {
      outputs_bucket = local.automation_bucket_name
    }
  }
}

output "automation_bucket_name" {
  description = "GCS bucket where Terraform automation artifacts are managed"
  value       = local.automation_bucket_name
}

output "automation_sa_email" {
  description = "The email of the automation service account"
  value       = local.automation_sa_email
}

resource "google_storage_bucket_object" "providers" {
  for_each = local.providers
  bucket   = module.automation_gcs.name
  name     = "providers/${each.key}.tf"
  content  = each.value
}

resource "google_storage_bucket_object" "tfvars" {
  bucket  = module.automation_gcs.name
  name    = "tfvars/0-bootstrap.auto.tfvars.json"
  content = jsonencode(local.tfvars)
}
