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

variable "prefix" {
  description = "Prefix used for resource names."
  type        = string
  default     = ""
  nullable    = false
}

variable "cluster_name" {
  description = "Name of the GKE cluster."
  type        = string
  nullable    = false
}

variable "cluster_location" {
  description = "Location of the GKE cluster."
  type        = string
  nullable    = false
}

variable "project_id" {
  description = "Project id of existing or created project."
  nullable    = false
  type        = string
}

variable "namespace" {
  description = "Namespace for the service account."
  type        = string
  nullable    = false
  default     = "saxml"
}

variable "ksa_name" {
  description = "Name for the Kubernetes Service Account"
  type        = string
  nullable    = false
  default     = "saxml-ksa"
}

variable "wid_sa_name" {
  description = "Name for the workload identity Google Service Account"
  type        = string
  nullable    = false
  default     = "saxml-wid-sa"
}

variable "wid_sa_roles" {
  description = "Roles to assign to a wid service account"
  type        = list(string)
  default     = ["storage.admin", "logging.logWriter"]
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
