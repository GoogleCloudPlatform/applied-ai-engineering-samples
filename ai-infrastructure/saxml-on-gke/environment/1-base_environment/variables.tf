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


variable "gcs_configs" {
  description = "Configs for Saxml root and model repository buckets"
  type = map(object({
    admin-root       = {}
    model-repository = {}
  }))
}

variable "node_pool_sa_name" {
  description = "The name of the node pool service account"
  type        = string
  default     = "node-pool-sa"
  nullable    = false
}

variable "wid_sa_name" {
  description = "The name of the workload identify sa"
  type        = string
  default     = "wid-sa"
  nullable    = false
}

variable "cluster_config" {
  description = "GKE cluster configs"
  type = object({
    name                = optional(string, "saxml-gke")
    workloads_namespace = optional(string, "saxml")
  })
}


variable "cpu_node_pools" {
  description = "Configurations for a CPU node pool"
  type = map(object({
    zones          = list(string)
    min_node_count = number
    max_node_count = number
    machine_type   = string
  }))
  nullable = false
}

variable "tpu_node_pools" {
  description = "Configurations for a TPU node pools"
  type = map(object({
    zones          = list(string)
    min_node_count = number
    max_node_count = number
    tpu_type       = string
  }))
  nullable = false
}



