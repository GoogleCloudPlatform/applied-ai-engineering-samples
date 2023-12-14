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

variable "node_pool_sa_name" {
  description = "The name of the node pool service account"
  type        = string
  default     = "saxml-node-pool-sa"
  nullable    = false
}

variable "wid_sa_name" {
  description = "The name of the workload identify sa"
  type        = string
  default     = "saxml-wid-sa"
  nullable    = false
}

variable "artifact_registry_name" {
  description = "The name of the Artifact Registry"
  type        = string
  default     = null
  nullable    = true
}

variable "artifact_registry_location" {
  description = "The location of the Artifact Registry"
  type        = string
  default     = "us"
  nullable    = true
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
  default = {
    saxml-admin-node-pool = {
      zones          = ["us-central2-a"]
      min_node_count = 1
      max_node_count = 1
      machine_type   = "n1-standard-8"
      disk_size_gb   = 100
      taints = {
        saxml-admin-node-pool = {
          value  = true
          effect = "NO_SCHEDULE"
        }
      }
      labels = {
        saxml-admin-node-pool = true
      }
    }

    default-node-pool = {
      zones          = ["us-central2-a"]
      min_node_count = 1
      max_node_count = 3
      machine_type   = "n1-standard-8"
      disk_size_gb   = 200
      taints         = {}
      labels         = {}
    }

    large-workloads-node-pool = {
      zones          = ["us-central2-a"]
      min_node_count = 0
      max_node_count = 3
      machine_type   = "n2-highmem-32"
      disk_size_gb   = 500
      taints         = {}
      labels         = {}
    }

    saxml-proxy-node-pool = {
      zones          = ["us-central2-a"]
      min_node_count = 1
      max_node_count = 3
      machine_type   = "n1-standard-8"
      disk_size_gb   = 100
      taints = {
        saxml-proxy-node-pool = {
          value  = true
          effect = "NO_SCHEDULE"
        }
      }
      labels = {
        saxml-proxy-node-pool = true
      }
    }
  }
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
    network_name = "saxml-gke-cluster-network"
    subnet_name  = "saxml-gke-cluster-subnet"
  }
}



