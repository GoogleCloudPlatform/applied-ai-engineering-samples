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

variable "tensorboard_region" {
  description = "The region for a Vertex Tensorboard instance "
  default     = "us-central1"
}

variable "tensorboard_config" {
  description = "Tensorboard instance configuration"
  type = object({
    name        = optional(string, "LLM Training")
    description = optional(string, "TPU on GKE training monitoring")
    region      = string
  })
  nullable = true
  default  = null
}
variable "tensorboard_name" {
  description = "The Tensorboard instance display name"
  default     = "TPU on GKE training experiments"
  nullable    = false
}

variable "tensorboard_description" {
  description = "The Tensorboard instance display name"
  default     = "TPU on GKE training experiments"
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

variable "artifact_repository_name" {
  description = "The name of the artifact repository bucket"
  type        = string
  default     = "artifact-repository"
  nullable    = false
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

variable "cluster_name" {
  description = "The name of the cluster"
  type        = string
  default     = "tpu-training-cluster"
  nullable    = false
}

variable "vpc_config" {
  description = "VPC configuration"
  type = object({
    network_name = optional(string, "training-gke-network")
    subnet_name  = optional(string, "training-gke-subnetwork")
  })
  nullable = false
  default  = {}
}

variable "cpu_node_pools" {
  description = "The configuration parameters for a CPU node pool"
  type = map(object({
    zones          = list(string)
    min_node_count = optional(number, 1)
    max_node_count = optional(number, 3)
    machine_type   = optional(string, "n1-standard-8")
    gcfs           = optional(string, true)
  }))
  nullable = false
}

variable "tpu_node_pools" {
  description = "Configurations for TPU node pools"
  type = map(object({
    zones          = list(string)
    min_node_count = number
    max_node_count = number
    tpu_type       = string
  }))
  nullable = false
}



