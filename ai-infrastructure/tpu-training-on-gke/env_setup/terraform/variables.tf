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
}

variable "region" {
    description = "The region for a GKE cluster and a GCS bucket"
    type        = string
}

variable "tensorboard_region" {
    description = "The region for a Vertex Tensorboard instance "
    default     = "us-central1" 
}

variable "tensorboard_name" {
    description = "The Tensorboard instance display name"
    default     = "TPU on GKE training experiments" 
}

variable "zone" {
    description = "The  zone for GKE node pools"
    type        = string
}


variable "artifact_repository_bucket_name" {
    description = "The GCS bucket name to be used as artifact repository"
    type        = string
}

variable "force_destroy" {
    description = "Force destroy flag for the GCS bucket"
    default = true 
}

variable "network_name" {
    description = "The network name"
    type        = string
}

variable "subnet_name" {
    description = "The subnet name"
    type        = string
}

variable "subnet_ip_range" {
  description = "The IP address range for the subnet"
  default     = "10.129.0.0/20"
}

variable "pods_ip_range" {
    description = "The secondary IP range for pods"
    default     = "192.168.64.0/20"
}

variable "services_ip_range" {
    description = "The secondary IP range for services"
    default     = "192.168.80.0/20"
}


variable "cluster_name" {
    description = "The name of the GKE cluster"
    type        = string
}

variable "gke_release_channel" {
    description = "GKE release channel"
    default = "STABLE"
}

variable "gke_version" {
    description = "GKE version"
    default      = "1.27.3-gke.100"
}

variable "cluster_description" {
    description = "The cluster's description"
    default = "GKE cluster for running TPU training workloads"
}


variable "cpu_pool_node_count" {
    description = "The number of nodes in the CPU node pool"
    default     = 3
}

variable "cpu_pool_machine_type" {
    description = "Machine type for nodes in the CPU node pool"
    default     = "n1-standard-4"
}

variable "cpu_pool_disk_type" {
    description = "Disk type for nodes in the CPU node pool"
    default = "pd-standard"
}

variable "cpu_pool_disk_size" {
    description = "Disk size for nodes in the CPU node pool"
    default = 200 
}


variable "tpu_sa_name" {
    description = "The service account name for TPU workload identity."
    default = "cloud-tpu-sa"
}

variable "tpu_sa_roles" {
  description = "The roles to assign to the TPU service account"
  default = [
    "roles/storage.objectAdmin",
    "roles/logging.logWriter",
    "roles/aiplatform.user",
    "roles/artifactregistry.reader"
    ] 
}

variable "gke_sa_name" {
    description = "The service account name for GKE node pools"
    default = "gke-sa"
}

variable "gke_sa_roles" {
  description = "The roles to assign to the GKE service account"
  default = [
    "storage.objectAdmin",
    "logging.logWriter",
    "aiplatform.user",
    "artifactregistry.reader"
    ] 
}

variable "tpu_namespace" {
    description = "The K8s namespace for TPU workloads."
    default = "tpu-training"
}

variable "max_pods_per_node" {
    description = "The maximum number of pods to schedule per node"
    default     = 110 
}


variable "tpu_machine_type" {
    description = "TPU machine type"
    default = "ct4p-hightpu-4t"
}

variable "tpu_type" {
    description = "TPU type"
    default = "v4-16"
}

variable "tpu_topology" {
    description = "TPU slice topology"
    default = "2x2x2"
}

variable "enable_tpu_autoscaling" {
    description = "Enable TPU autoscaling"
    default = false 
}

variable "tpu_num_nodes" {
    description = "Number of hosts in a TPU slice"
    default = 2 
}

variable "tpu_node_pool_name_prefix" {
    description = "TPU node pools name prefix"
    default = "tpu-node-pool" 
}

variable "num_tpu_pools" {
    description = "Number of TPU slices to create"
    default = 1 
}

variable "multislice_group_name" {
    description = "A name of a multislice group"
    default = "multi-slice-group"
}
