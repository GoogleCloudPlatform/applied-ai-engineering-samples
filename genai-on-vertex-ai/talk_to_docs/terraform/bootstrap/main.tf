resource "google_project_service" "project_service" {
  for_each           = toset(var.services)
  disable_on_destroy = false
  service            = each.key
}

resource "google_service_account" "cloudbuild_service_account" {
  account_id   = var.cloudbuild_sa_name
  description  = "Cloud Build service account for the T2X service."
  display_name = "T2X Cloud Build"
}

resource "google_project_iam_member" "cloudbuild_service_account" {
  for_each = toset(var.cloudbuild_iam_roles)
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_service_account_iam_member" "cloudbuild_terraform_token_creator" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/${var.terraform_service_account}"
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_storage_bucket" "staging_bucket" {
  name                        = "${var.staging_bucket_prefix}-${var.project_id}"
  location                    = "US"
  force_destroy               = true
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "staging_bucket_data_mover" {
  count  = var.data_mover_service_account != null ? 1 : 0
  bucket = google_storage_bucket.staging_bucket.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${var.data_mover_service_account}"
}

resource "google_artifact_registry_repository" "talk_to_docs" {
  repository_id = "talk-to-docs"
  format        = "DOCKER"
  location      = var.region
  description   = "talk-to-docs Docker repository"
}
