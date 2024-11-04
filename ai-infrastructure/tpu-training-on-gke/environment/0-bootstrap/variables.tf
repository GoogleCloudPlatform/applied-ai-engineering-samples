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

variable "deletion_protection" {
  description = "Prevent Terraform from destroying the provisioned automation bucket"
  type        = bool
  default     = true
  nullable    = false
}

variable "create_automation_sa" {
  description = "Whether to create an automation service account"
  type        = bool
  default     = true
  nullable    = false
}

variable "create_automation_bucket" {
  description = "Whether to create an automation bucket"
  type        = bool
  default     = true
  nullable    = false
}

variable "enable_apis" {
  description = "Whether to attempt to enable APIs on the project"
  type        = bool
  default     = true
  nullable    = false
}

variable "automation_bucket" {
  description = "The parameters of the bucket to be used by automation tools including Terraform backend"
  type = object({
    name     = string
    location = string
  })
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "automation_sa_name" {
  description = "The name of the automation service account"
  type        = string
}

variable "services" {
  description = "Services to enable in the project"
  type        = list(string)
  default     = []
  nullable    = false
}

variable "roles" {
  description = "Project level roles to add to an automation account"
  type        = list(string)
  default     = []
  nullable    = false
}
