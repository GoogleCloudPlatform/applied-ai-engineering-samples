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

resource "docker_image" "dataflow-image" {
  provider = docker.private
  name     = "${google_artifact_registry_repository.rag_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.rag_repo.name}/dataflow-template:latest"
  build {
    context = "../backend/data_processing_pipeline_beam/"  
  }
}

resource "docker_registry_image" "dataflow" {
  provider      = docker.private
  name          = docker_image.dataflow-image.name
  keep_remotely = true
}

module "gcloud" {
  source  = "terraform-google-modules/gcloud/google"
  version = "3.4.1"
  platform              = "linux"
  additional_components = ["beta"]
  skip_download         = false  # Skip downloading gcloud if it's already available
  upgrade = true
  # create_cmd_entrypoint = "bash"
  create_cmd_body       = "beta dataflow flex-template build gs://${var.project_id}-rag/${var.dataflow_metadata_filename} --image ${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_id}/dataflow-template:latest --sdk-language PYTHON"
  module_depends_on     = [docker_registry_image.dataflow]
}

resource "google_dataflow_flex_template_job" "dataflow_template_job" {
  provider                = google-beta
  name                    = var.dataflow_job_name
  container_spec_gcs_path = "gs://${var.project_id}-rag/${var.dataflow_metadata_filename}"
  parameters = {
    input_subscription = "projects/${var.project_id}/subscriptions/${var.input_topic_subscription_name}"
    output_topic       = "projects/${var.project_id}/topics/${var.output_topic_name}"
  }
  depends_on = [module.gcloud, google_pubsub_topic.output, google_pubsub_subscription.input-subscription]
}