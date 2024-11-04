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
  description = "The name of the GKE cluster."
  type        = string
  nullable    = false
}

variable "location" {
  description = "The location of the GKE cluster."
  type        = string
  nullable    = false
}

variable "namespace" {
  description = "The namespace for Kueue local queue."
  type        = string
  nullable    = false
}

variable "cluster_queue_name" {
  description = "The name of the Kueue ClusterQueue."
  type        = string
  nullable    = false
}

variable "local_queue_name" {
  description = "The name of the Kueue LocalQueue"
  type        = string
  nullable    = false
}

variable "tpu_resources" {
  description = "TPU resources for Kueue."
  type = list(object({
    name      = string,
    num_chips = number
  }))
  default = []
}
