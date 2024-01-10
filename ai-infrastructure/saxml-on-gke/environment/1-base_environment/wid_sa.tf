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


locals {
  gcp_sa_static_id        = "projects/${var.project_id}/serviceAccounts/${module.wid_service_account.email}"
  k8s_sa_gcp_derived_name = "serviceAccount:${var.project_id}.svc.id.goog[${var.wid_sa.ksa_namespace}/${var.wid_sa.ksa_name}]"
}

module "wid_service_account" {
  source       = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account?ref=v28.0.0&depth=1"
  project_id   = var.project_id
  name         = local.wid_sa.name
  display_name = local.wid_sa.description
  iam_project_roles = {
    "${var.project_id}" = [for role in local.wid_sa.roles : "roles/${role}"]
  }
}


resource "google_service_account_iam_member" "wid_role" {
  service_account_id = local.gcp_sa_static_id
  role               = "roles/iam.workloadIdentityUser"
  member             = local.k8s_sa_gcp_derived_name
}
