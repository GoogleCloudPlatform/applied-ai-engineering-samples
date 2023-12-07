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

provider "kubernetes" {
  host                   = "https://${module.cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.cluster.ca_certificate)
}

locals {
  namespace               = var.cluster_config.workloads_namespace
  ksa_name                = local.wid_sa_name
  gcp_sa_name             = local.wid_sa_name
  gcp_sa_static_id        = "projects/${var.project_id}/serviceAccounts/${local.wid_sa_email}"
  gcp_sa_email            = local.wid_sa_email
  k8s_sa_gcp_derived_name = "serviceAccount:${var.project_id}.svc.id.goog[${local.namespace}/${local.ksa_name}]"
}

resource "kubernetes_namespace" "namespace" {
  metadata {
    name = local.namespace
  }
}

resource "kubernetes_service_account" "ksa" {

  automount_service_account_token = false
  metadata {
    name      = local.ksa_name
    namespace = kubernetes_namespace.namespace.metadata[0].name
    annotations = {
      "iam.gke.io/gcp-service-account" = local.gcp_sa_email
    }
  }
}

resource "google_service_account_iam_member" "main" {
  service_account_id = local.gcp_sa_static_id
  role               = "roles/iam.workloadIdentityUser"
  member             = local.k8s_sa_gcp_derived_name
}
