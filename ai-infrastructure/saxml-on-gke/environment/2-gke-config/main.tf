
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



module "wid" {
  source       = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/workload-identity?ref=workload-identity"
  cluster_name = var.cluster_name
  location     = var.cluster_location
  project_id   = var.project_id
  wid_sa_name  = var.wid_sa_name
  ksa_name     = var.ksa_name
  namespace    = var.namespace
}
