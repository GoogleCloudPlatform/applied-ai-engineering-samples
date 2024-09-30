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

resource "google_project_service" "default" {
  service            = "workflows.googleapis.com"
  disable_on_destroy = false
}

resource "google_workflows_workflow" "default" {
  name            = var.workflow_name
  region          = var.region
  service_account = google_service_account.workflow_account.id
  description     = "RAG Playground workflow"
  labels = {
    env = "test"
  }
  source_contents = templatefile("main.yaml",{fn_url_ans_gen=google_cloudfunctions2_function.rag_playground_cloud_functions["source_ans_gen_service"].url, fn_url_rp_eval=google_cloudfunctions2_function.rag_playground_cloud_functions["source_rp_eval_service"].url})
  depends_on = [google_project_service.default, google_cloudfunctions2_function.rag_playground_cloud_functions]    
}