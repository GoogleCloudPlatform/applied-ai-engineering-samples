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
      "aiplatform.user",
      "artifactregistry.reader",
    ]
  }
}

variable "wid_sa" {
  description = "The config for a workload identity service account"
  type = object({
    name          = string
    description   = string
    roles         = list(string)
    ksa_namespace = string
    ksa_name      = string
  })
  default = {
    name          = "gke-wid-sa"
    description   = "GKE Wid service account"
    ksa_namespace = "tpu-training"
    ksa_name      = "wid-sa"
    roles = [
      "storage.objectAdmin",
      "logging.logWriter",
      "aiplatform.user",
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
    name     = "training-images"
    location = "us"
  }
}

variable "gcs_configs" {
  description = "GCS storage configs"
  type        = map(map(any))
  default = {
    "artifact-repository" = {}
  }
}

variable "cluster_config" {
  description = "GKE cluster configs"
  type        = map(any)
  default = {
    name                = "gke-ml-cluster"
    workloads_namespace = "training"
  }
}

variable "cpu_node_pools" {
  description = "Configurations for a CPU node pool"
  type = map(object({
    zones          = list(string)
    min_node_count = optional(number, 3)
    max_node_count = optional(number, 3)
    machine_type   = optional(string, "n1-standard-16")
    disk_size_gb   = optional(number, 200)
    labels         = optional(map(string), {})
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
  }))
  validation {
    condition = alltrue([
      for tpu_type in [for name, node_pool in var.tpu_node_pools : node_pool.tpu_type] :
      contains(
        [
          "v5litepod-16",
          "v5litepod-32",
          "v5litepod-64",
          "v5litepod-128",
          "v5litepod-256",
          "v4-8",
          "v4-16",
          "v4-32",
          "v4-64",
          "v4-128",
          "v4-256",
          "v4-512",
          "v4-1024",
          "v4-1536",
          "v4-2048",
          "v4-4096"
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
    network_name = "gke-cluster-network"
    subnet_name  = "gke-cluster-subnet"
  }
}

variable "tensorboard_config" {
  description = "Tensorboard instance configuration"
  type = object({
    name        = optional(string, "TPU Training")
    description = optional(string, "TPU on GKE training monitoring")
    region      = string
  })
  nullable = true
  default  = null
}
