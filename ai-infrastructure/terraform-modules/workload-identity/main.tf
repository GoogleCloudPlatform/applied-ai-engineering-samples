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

data "google_service_account" "gsa" {
  count      = var.google_service_account_create ? 0 : 1
  account_id = var.google_service_account
  project    = var.project_id
}

data "google_container_cluster" "gke_cluster" {
  project  = var.project_id
  name     = var.cluster_name
  location = var.location
}

provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.gke_cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(data.google_container_cluster.gke_cluster.master_auth[0].cluster_ca_certificate)
}


locals {
  wid_sa_email = (
    var.google_service_account_create
    ? module.workload-service-account.0.email
    : data.google_service_account.gsa.0.email
  )
  wid_sa_name = (
    var.google_service_account_create
    ? module.workload-service-account.0.name
    : data.google_service_account.gsa.0.name
  )
}

module "workload-service-account" {
  source      = "github.com/GoogleCloudPlatform/cloud-foundation-fabric.git//modules/iam-service-account?ref=v29.0.0&depth=1"
  count       = var.google_service_account_create ? 1 : 0
  project_id  = var.project_id
  name        = var.google_service_account
  description = "Service account for GKE workloads"
}

resource "google_service_account_iam_member" "ksa-bind-to-gsa" {
  service_account_id = local.wid_sa_name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.namespace}/${var.kubernetes_service_account}]"
}

resource "kubernetes_namespace" "namespace" {
  count = var.namespace_create ? 1 : 0
  metadata {
    annotations = {
      name = var.namespace
    }
    name = var.namespace
  }
}

resource "kubernetes_service_account" "ksa" {
  metadata {
    name      = var.kubernetes_service_account
    namespace = var.namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = "${local.wid_sa_email}"
    }
  }
  depends_on = [module.workload-service-account,
    kubernetes_namespace.namespace
  ]
}
