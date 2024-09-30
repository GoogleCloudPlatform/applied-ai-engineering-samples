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

resource "google_service_account" "rag_sa_account" {
  account_id   = var.rag_playground_sa_id
  display_name = var.rag_playground_sa_display_name
}

resource "google_project_iam_member" "datastore_owner" {
  project = var.project_id
  role    = "roles/datastore.owner"
  member  = "serviceAccount:${google_service_account.rag_sa_account.email}"
}

# Add Vertex AI Admin role
resource "google_project_iam_member" "vertexai_admin" {
  project = var.project_id
  role    = "roles/aiplatform.admin"
  member  = "serviceAccount:${google_service_account.rag_sa_account.email}"
}

# Add Cloud Storage Admin role
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.rag_sa_account.email}"
}

# Add Vertex AI Rapid Eval Service Agent role
resource "google_project_iam_member" "rapid_eval_service_agent" {
  project = var.project_id
  role    = "roles/aiplatform.rapidevalServiceAgent"
  member  = "serviceAccount:${google_service_account.rag_sa_account.email}"
}

resource "google_service_account" "workflow_account" {
  account_id   = var.rag_workflow_sa_id
  display_name = var.rag_workflow_sa_display_name
}

# Add Cloud Run Invoker role
resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.workflow_account.email}"
}