
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

data "google_client_config" "default" {}

data "google_container_cluster" "gke_cluster" {
  project  = var.project_id
  name     = var.cluster_name
  location = var.cluster_location
}

provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.gke_cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(data.google_container_cluster.gke_cluster.master_auth[0].cluster_ca_certificate)
}

locals {
  wid_sa_name = (
    var.prefix != ""
    ? "${var.prefix}-${var.wid_sa_name}"
    : var.wid_sa_name
  )
}

module "wid" {
  source       = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/workload-identity?ref=main"
  cluster_name = var.cluster_name
  location     = var.cluster_location
  project_id   = var.project_id
  wid_sa_name  = local.wid_sa_name
  wid_sa_roles = var.wid_sa_roles
  ksa_name     = var.ksa_name
  namespace    = var.namespace
}
