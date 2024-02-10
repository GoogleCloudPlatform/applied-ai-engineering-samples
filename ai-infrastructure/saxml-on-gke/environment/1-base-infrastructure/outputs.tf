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
  tfvars = {
    cluster_name     = module.base_environment.cluster_name
    cluster_location = module.base_environment.cluster_region
    project_id       = var.project_id
  }

  environment_settings = {
    project_id                   = var.project_id
    cluster_name                 = module.base_environment.cluster_name
    cluster_location             = module.base_environment.cluster_region
    cluster_endpoint             = module.base_environment.cluster_endpoint
    gcs_buckets                  = module.base_environment.gcs_buckets
    node_pool_sa_email           = module.base_environment.node_pool_sa_email
    artifact_registry_image_path = try(module.base_environment.artifact_registry_image_path)
    locust_dataset_id            = try(google_bigquery_dataset.locust_dataset[0].id, null)
    locust_metrics_table_id      = try(google_bigquery_table.locust_metrics[0].id, null)
    locust_metrics_topic_id      = try(google_pubsub_topic.locust_sink[0].id, null)
    locust_metrics_topic_name    = try(google_pubsub_topic.locust_sink[0].name, null)
  }
}

output "cluster_name" {
  value = module.base_environment.cluster_name
}

output "cluster_endpoint" {
  value = module.base_environment.cluster_endpoint
}

output "cluster_region" {
  value = var.region
}

output "gcs_buckets" {
  value = module.base_environment.gcs_buckets
}

output "artifact_registry_image_path" {
  description = "The URI of an Artifact Registry if created"
  value       = try(module.base_environment.artifact_registry_image_path, null)
}

output "locust_dataset_id" {
  description = "Locust metrics dataset id"
  value       = try(google_bigquery_dataset.locust_dataset[0].id, null)
}

output "locust_metrics_table_id" {
  description = "Locust metrics table id"
  value       = try(google_bigquery_table.locust_metrics[0].id, null)
}

output "locust_metrics_topic_id" {
  description = "Locust metrics topic ID"
  value       = try(google_pubsub_topic.locust_sink[0].id, null)
}

output "locust_metrics_topic_name" {
  description = "Locust metrics topic name"
  value       = try(google_pubsub_topic.locust_sink[0].name, null)
}

output "locust_metrics_bq_subscription" {
  description = "Locust metrics BQ subscription"
  value       = try(google_pubsub_subscription.locust_bq_subscription[0].id, null)
}

resource "google_storage_bucket_object" "tfvars" {
  for_each = var.automation.outputs_bucket == null ? {} : { 1 = 1 }
  name     = "tfvars/1-base-infra.auto.tfvars.json"
  bucket   = var.automation.outputs_bucket
  content  = jsonencode(local.tfvars)
}

resource "google_storage_bucket_object" "environment_settings" {
  for_each = var.automation.outputs_bucket == null ? {} : { 1 = 1 }
  name     = "settings/1-base-infra-settings.json"
  bucket   = var.automation.outputs_bucket
  content  = jsonencode(local.environment_settings)
}
