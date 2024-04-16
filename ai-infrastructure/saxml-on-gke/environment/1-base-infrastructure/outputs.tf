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
    prefix           = var.prefix
  }

  environment_settings = {
    project_id                   = var.project_id
    cluster_name                 = module.base_environment.cluster_name
    cluster_location             = var.region
    cluster_endpoint             = module.base_environment.cluster_endpoint
    gcs_buckets                  = module.base_environment.gcs_buckets
    node_pool_sa_email           = module.base_environment.node_pool_sa_email
    artifact_registry_image_path = module.base_environment.artifact_registry_image_path
    metrics_dataset_id           = try(module.performance_metrics_infra[0].performance_metrics_dataset_id, null)
    metrics_table_id             = try(module.performance_metrics_infra[0].performance_metrics_table_id, null)
    metrics_topic_id             = try(module.performance_metrics_infra[0].performance_metrics_topic_id, null)
    metrics_topic_name           = try(module.performance_metrics_infra[0].performance_metrics_topic_name, null)
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

output "node_pool_sa_email" {
  value = module.base_environment.node_pool_sa_email
}
output "gcs_buckets" {
  value = module.base_environment.gcs_buckets
}

output "artifact_registry_image_path" {
  description = "The URI of an Artifact Registry if created"
  value       = module.base_environment.artifact_registry_image_path
}

output "metrics_dataset_id" {
  description = "Performance metrics dataset id"
  value       = try(module.performance_metrics_infra[0].performance_metrics_dataset_id, null)
}

output "metrics_table_id" {
  description = "Performance metrics table id"
  value       = try(module.performance_metrics_infra[0].performance_metrics_table_id, null)
}

output "metrics_topic_id" {
  description = "Performance metrics topic ID"
  value       = try(module.performance_metrics_infra[0].performance_metrics_topic_id, null)
}

output "metrics_topic_name" {
  description = "Performance metrics topic name"
  value       = try(module.performance_metrics_infra[0].performance_metrics_topic_name, null)
}

output "metrics_bq_subscription" {
  description = "Performance metrics BQ subscription"
  value       = try(module.performance_metrics_infra[0].performance_metrics_bq_subscription, null)
}

resource "google_storage_bucket_object" "tfvars" {
  for_each = var.automation.outputs_bucket == null ? {} : { 1 = 1 }
  name     = "${var.env_name}/tfvars/1-base-infra.auto.tfvars.json"
  bucket   = var.automation.outputs_bucket
  content  = jsonencode(local.tfvars)
}

resource "google_storage_bucket_object" "environment_settings" {
  for_each = var.automation.outputs_bucket == null ? {} : { 1 = 1 }
  name     = "${var.env_name}/settings/1-base-infra-settings.json"
  bucket   = var.automation.outputs_bucket
  content  = jsonencode(local.environment_settings)
}
