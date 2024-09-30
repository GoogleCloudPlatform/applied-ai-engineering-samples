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

resource "google_firestore_database" "rag_playground_database" {
  project                  = var.project_id
  location_id              = var.region
  name                      = var.firestore_database_name
  type                      = var.firestore_database_type
  concurrency_mode         = var.firestore_concurrency_mode
  app_engine_integration_mode = var.firestore_app_engine_integration_mode
  point_in_time_recovery_enablement = var.firestore_point_in_time_recovery_enablement
  delete_protection_state    = var.firestore_delete_protection_state
  deletion_policy           = var.firestore_deletion_policy
}

locals {
  config_json = jsondecode(file(var.firebase_config_file_path))
}

resource "google_firestore_document" "config" {
  project     = var.project_id
  database    = google_firestore_database.rag_playground_database.name
  collection  = var.firestore_collection_name
  document_id = var.firestore_document_id
  depends_on = [google_firestore_database.rag_playground_database]
  fields      = jsonencode({
    for key, value in local.config_json : key => {
        mapValue = {
            fields = {
                for k, v in value : k => {
                    stringValue = v
                }
            }
        }
    }
  })
}