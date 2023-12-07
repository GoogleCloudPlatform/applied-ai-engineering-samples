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


variable "project_id" {
  description = "The GCP project ID"
  type        = string
  nullable    = false
}

variable "region" {
  description = "The region for the environment"
  type        = string
  nullable    = false
}

variable "deletion_protection" {
  description = "Prevent Terraform from destroying data storage resources (storage buckets, GKE clusters). When this field is set, a terraform destroy or terraform apply that would delete data storage resources will fail."
  type        = bool
  default     = true
  nullable    = false
}

variable "prefix" {
  description = "Prefix used for resource names."
  type        = string
  default     = ""
  nullable    = false
}

#variable "sa_email" {
#  description = "The email of the service account to have owner rights on BQ dataset"
#  type        = string
#  nullable    = false
#}

variable "pubsub_config" {
  description = "The settings for Pubsub topic and subscription"
  type = object({
    topic_name        = optional(string, "locust_pubsub_sink")
    subscription_name = optional(string, "locust_pubsub_bq_sub")
    schema_name       = optional(string, "locust_metrics_schema")
  })
  nullable = false
  default  = {}
}

variable "bq_config" {
  description = "The settings for BigQuery dataset and tables"
  type = object({
    dataset_name = optional(string, "locust_metrics_dataset")
    location     = optional(string, "US")
    table_name   = optional(string, "locust_metrics")
  })
  nullable = false
  default  = {}
}
