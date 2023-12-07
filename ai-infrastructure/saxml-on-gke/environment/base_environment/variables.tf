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

variable "gcs_configs" {
  description = "The configs for GCS buckets"
  type = map(object({
    versioning    = optional(bool, false)
    location      = optional(string, "")
    storage_class = optional(string, "STANDARD")
    iam           = optional(list(string), ["storage.legacyBucketReader"])
  }))
  default  = {}
  nullable = false
}

variable "registry_config" {
  description = "The configs for Artifact registry"
  type = object({
    name = string
  })
  default  = null
  nullable = true
}

variable "node_pool_sa" {
  description = "The config for a node pool service account. If email is set the existing service account is used. If name is a new account is created. If roles are null the default roles are used."
  type = object({
    name  = optional(string, "gke-node-pool-sa")
    email = optional(string, "")
    roles = optional(list(string), [
      "storage.objectAdmin",
      "logging.logWriter",
      "pubsub.publisher",
    ])
    description = optional(string, "GKE workload identity service account")
  })
  default = {
  }
  validation {
    condition     = !(var.node_pool_sa.email == "" && var.node_pool_sa.name == "")
    error_message = "Either email or name must be set."
  }
  nullable = false
}

variable "wid_sa" {
  description = "The config for a workload identity service account. If email is set the existing service account is used. If name is a new account is created. If roles are null the default roles are used."
  type = object({
    name  = optional(string, "gke-wid-sa")
    email = optional(string, "")
    roles = optional(list(string), [
      "storage.objectAdmin",
      "logging.logWriter",
      "pubsub.publisher",
    ])
    description = optional(string, "GKE node pool service account")
  })
  default = {
  }
  validation {
    condition     = !(var.wid_sa.email == "" && var.wid_sa.name == "")
    error_message = "Either email or name must be set."
  }
  nullable = false
}

variable "vpc_ref" {
  description = "Network configurations of an existing VPC to use for the environment. If null a new VPC based on the provided network_config will be created"
  type = object({
    host_project           = string
    network_self_link      = string
    subnet_self_link       = string
    pods_ip_range_name     = string
    services_ip_range_name = string
  })
  default = null
}

variable "vpc_config" {
  description = "Network configurations of a VPC to create. Must be specified if vpc_reg is null"
  type = object({
    network_name           = optional(string, "gke-cluster-network")
    subnet_name            = optional(string, "gke-cluster-subnetwork")
    subnet_ip_cidr_range   = optional(string, "10.129.0.0/20")
    pods_ip_cidr_range     = optional(string, "192.168.64.0/20")
    services_ip_cidr_range = optional(string, "192.168.80.0/20")
    routing_mode           = optional(string, "REGIONAL")
    nat_router_name        = optional(string, "nat-router")
  })
  default  = {}
  nullable = false
}


variable "cluster_config" {
  description = "Base cluster configurations"
  type = object({
    name                           = optional(string, "gke-ml-cluster")
    release_channel                = optional(string, "REGULAR")
    version                        = optional(string, "1.27.5-gke.200")
    description                    = optional(string, "GKE ML inference cluster")
    gcs_fuse_csi_driver            = optional(bool, true)
    gce_persistent_disk_csi_driver = optional(bool, true)
    workload_identity              = optional(bool, true)
    workloads_namespace            = optional(string, "serving-workloads")
    enable_workload_logs           = optional(bool, true)
    enable_scheduler_logs          = optional(bool, true)
    enable_controller_manager_logs = optional(bool, true)
    enable_api_server_logs         = optional(bool, true)
  })
  default  = {}
  nullable = false
}

variable "cpu_node_pools" {
  description = "Configurations for CPU node pools"
  type = map(object({
    zones          = list(string)
    min_node_count = number
    max_node_count = number
    machine_type   = string
    gcfs           = optional(bool, true)
    gvnic          = optional(bool, true)
    disk_type      = optional(string, "pd-standard")
    disk_size_gb   = optional(string, 200)
    auto_repair    = optional(bool, true)
    auto_upgrade   = optional(bool, true)
    oauth_scopes   = optional(list(string), ["https://www.googleapis.com/auth/cloud-platform"])
    taints = optional(map(object({
      value  = string
      effect = string
    })), {})
    labels = optional(map(string), {})
  }))
  validation {
    condition = alltrue([
      for k, v in merge([for name, node_pool in var.cpu_node_pools : node_pool.taints]...) :
      contains(["NO_SCHEDULE", "PREFER_NO_SCHEDULE", "NO_EXECUTE"], v.effect)
    ])
    error_message = "Invalid taint effect."
  }
  default  = {}
  nullable = false
}

variable "tpu_node_pools" {
  description = "Configurations for TPU node pools"
  type = map(object({
    zones          = list(string)
    min_node_count = number
    max_node_count = number
    tpu_type       = string
    disk_type      = optional(string, "pd-standard")
    disk_size_gb   = optional(string, 200)
    gvnic          = optional(bool, true)
    gcfs           = optional(bool, true)
    auto_repair    = optional(bool, true)
    auto_upgrade   = optional(bool, true)
    oauth_scopes   = optional(list(string), ["https://www.googleapis.com/auth/cloud-platform"])
    taints = optional(map(object({
      value  = string
      effect = string
    })), {})
    labels = optional(map(string), {})
  }))
  validation {
    condition = alltrue([
      for k, v in merge([for name, node_pool in var.tpu_node_pools : node_pool.taints]...) :
      contains(["NO_SCHEDULE", "PREFER_NO_SCHEDULE", "NO_EXECUTE"], v.effect)
    ])
    error_message = "Invalid taint effect."
  }
  default  = {}
  nullable = false
}

