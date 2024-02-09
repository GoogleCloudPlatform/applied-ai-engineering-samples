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
  gcs_storage_class = (
    length(split("-", var.automation_bucket.location)) < 2
    ? "MULTI_REGIONAL"
    : "REGIONAL"
  )

  default_services = [
    "accesscontextmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudkms.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "container.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "serviceusage.googleapis.com",
    "sourcerepo.googleapis.com",
    "stackdriver.googleapis.com",
    "storage-component.googleapis.com",
    "storage.googleapis.com",
    "sts.googleapis.com"
  ]
  services = concat(local.default_services, var.services)

  default_roles = [
    "roles/iam.securityAdmin",
    "roles/iam.serviceAccountAdmin",
    "roles/compute.networkAdmin",
    "roles/container.admin",
    "roles/iam.serviceAccountUser",
    "roles/storage.admin",
    "roles/artifactregistry.admin",
  ]
  roles = concat(local.default_roles, var.roles)

  automation_bucket_name = var.automation_bucket.name
  automation_sa_name     = var.automation_sa_name
  automation_sa_email    = "${var.automation_sa_name}@${var.project_id}.iam.gserviceaccount.com"
}

module "project_config" {
  count          = var.create_automation_resources ? 1 : 0
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=v29.0.0&depth=1"
  name           = var.project_id
  project_create = false
  services       = local.services
}

module "automation_gcs" {
  source        = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gcs?ref=v29.0.0&depth=1"
  project_id    = var.project_id
  name          = local.automation_bucket_name
  location      = var.automation_bucket.location
  storage_class = local.gcs_storage_class
  versioning    = true
  force_destroy = var.deletion_protection ? false : true
}

module "automation_sa" {
  count        = var.create_automation_resources ? 1 : 0
  source       = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account?ref=v29.0.0&depth=1"
  project_id   = var.project_id
  name         = local.automation_sa_name
  display_name = "Terraform automation service account."
  # allow SA used by CI/CD workflow to impersonate this SA
  #iam = {
  #  "roles/iam.serviceAccountTokenCreator" = compact([
  #    try(module.automation-tf-cicd-sa["bootstrap"].iam_email, null)
  #  ])
  #}
  iam_storage_roles = {
    (local.automation_bucket_name) = ["roles/storage.admin"]
  }
  iam_project_roles = {
    "${var.project_id}" = local.roles

  }
}

resource "google_storage_bucket_iam_binding" "bucket_permissions" {
  count  = var.create_automation_resources ? 0 : 1
  bucket = local.automation_bucket_name
  role   = "roles/storage.admin"
  members = [
    "serviceAccount:${local.automation_sa_email}",
  ]
}
