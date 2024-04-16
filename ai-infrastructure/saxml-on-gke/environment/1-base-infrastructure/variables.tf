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
  description = "The region for a GKE cluster and a GCS bucket"
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

variable "node_pool_sa" {
  description = "The config for a node pool service account"
  type = object({
    name        = string
    description = string
    roles       = list(string)
  })
  default = {
    name        = "gke-node-pool-sa"
    description = "GKE node pool service account"
    roles = [
      "storage.objectAdmin",
      "logging.logWriter",
      "artifactregistry.reader",
    ]
  }
}

variable "create_artifact_registry" {
  description = "Whether to create an Artifact Registry"
  type        = bool
  default     = true
}

variable "registry_config" {
  description = "The configs for Artifact registry"
  type = object({
    name     = string
    location = string
  })
  default = {
    name     = "serving-images"
    location = "us"
  }
}

variable "gcs_configs" {
  description = "GCS storage configs"
  type        = map(map(any))
  default = {
    "saxml-admin"            = {}
    "saxml-model-repository" = {}
  }
}

variable "cluster_config" {
  description = "GKE cluster configs"
  type        = map(any)
  default = {
    name                = "saxml-gke-cluster"
    workloads_namespace = "saxml"
  }
}

variable "cpu_node_pools" {
  description = "Configurations for a CPU node pool"
  type = map(object({
    zones          = list(string)
    min_node_count = number
    max_node_count = number
    machine_type   = string
    disk_size_gb   = number
    taints = map(object({
      value  = string
      effect = string
    }))
    labels = map(string)
  }))
  nullable = false
}

variable "tpu_node_pools" {
  description = "Configurations for a TPU node pools"
  type = map(object({
    zones        = list(string)
    tpu_type     = string
    disk_size_gb = optional(number, 200)
    autoscaling  = optional(bool, false)
    spot         = optional(bool, false)
  }))
  validation {
    condition = alltrue([
      for tpu_type in [for name, node_pool in var.tpu_node_pools : node_pool.tpu_type] :
      contains(
        [
          "v5litepod-1",
          "v5litepod-4",
          "v5litepod-8",
          "v5litepod-16",
          "v5litepod-32",
          "v5litepod-64",
          "v5litepod-128",
          "v5litepod-256",
        ],
        tpu_type
    )])
    error_message = "Unsupported TPU type"
  }
  nullable = false
}

variable "vpc_config" {
  description = "VPC configuration"
  type = object({
    network_name = string
    subnet_name  = string
  })
  default = {
    network_name = "saxml-gke-cluster-network"
    subnet_name  = "saxml-gke-cluster-subnet"
  }
}


variable "create_perf_testing_infrastructure" {
  description = "Whether to create BigQuery and Pubsub components to support performance testing"
  type        = bool
  default     = true
}


variable "pubsub_config" {
  description = "The settings for Pubsub topic and subscription"
  type = object({
    topic_name        = optional(string, "metrics_pubsub_sink")
    subscription_name = optional(string, "metrics_pubsub_bq_sub")
    schema_name       = optional(string, "metrics_schema")
  })
  nullable = false
  default  = {}
}

variable "bq_config" {
  description = "The settings for BigQuery dataset and tables"
  type = object({
    dataset_name = optional(string, "metrics_dataset")
    location     = optional(string, "US")
    table_name   = optional(string, "performance_metrics")
  })
  nullable = false
  default  = {}
}

variable "automation" {
  description = "Automation configs"
  type = object({
    outputs_bucket = string
  })
  default = {
    outputs_bucket = null
  }
  nullable = false
}

variable "env_name" {
  description = "The name of the folder in the automation bucket where auto.tfvars, setting files, etc will be stored."
  type        = string
  nullable    = false
  default     = "environment"
}
