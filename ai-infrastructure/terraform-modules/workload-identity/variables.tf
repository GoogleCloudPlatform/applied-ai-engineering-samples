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


variable "cluster_name" {
  description = "Name of the GKE cluster."
  type        = string
  nullable    = false
}

variable "location" {
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
}

variable "namespace_create" {
  description = "Create Kubernetes namespace"
  type        = bool
  default     = true
}

variable "kubernetes_service_account" {
  description = "Name for the Kubernetes Service Account to be used for benchmark"
  type        = string
  nullable    = false
}

variable "kubernetes_service_account_create" {
  description = "Create Kubernetes Service Account to be used for benchmark"
  type        = bool
  default     = true
}

variable "google_service_account" {
  description = "Name for the Google Service Account to be used for benchmark"
  type        = string
  nullable    = false
}

variable "google_service_account_create" {
  description = "Create Google service account to bind to a Kubernetes service account."
  type        = bool
  default     = true
}

