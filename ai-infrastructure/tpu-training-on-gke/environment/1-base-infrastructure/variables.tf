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
    name  = string
    roles = list(string)
  })
  default = {
    name = "gke-node-pool-sa"
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
    name  = string
    roles = list(string)
  })
  default = {
    name = "gke-wid-sa"
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
    min_node_count = number
    max_node_count = number
    machine_type   = string
    disk_size_gb   = number
    labels         = optional(map(string), {})
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
