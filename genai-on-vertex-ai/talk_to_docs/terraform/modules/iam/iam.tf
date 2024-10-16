locals {
  t2x_iam_roles = [
    "roles/aiplatform.user",
    "roles/bigquery.dataEditor",
    "roles/bigquery.user",
    "roles/discoveryengine.admin",
    "roles/gkemulticloud.telemetryWriter",
    "roles/storage.objectUser",
  ]

  workflow_iam_roles = [
    "roles/logging.logWriter",
    "roles/run.invoker",
  ]
}

resource "google_service_account" "t2x_service_account" {
  account_id   = "t2x-app"
  description  = "T2X app service-attached service account."
  display_name = "T2X App Service Account"
}

resource "google_project_iam_member" "t2x_service_account" {
  for_each = toset(local.t2x_iam_roles)
  project  = var.project_id
  role     = each.key
  member   = google_service_account.t2x_service_account.member
}

# Allow the IAP Service Agent to invoke Cloud Run services.
resource "google_project_iam_member" "iap_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = var.iap_sa_member
}

resource "google_service_account" "doc_ingestion_workflow" {
  account_id   = "doc-ingestion-workflow"
  description  = "Document Ingestion Workflow service account."
  display_name = "Document Ingestion Workflow Service Account"
}

resource "google_project_iam_member" "doc_ingestion_workflow" {
  for_each = toset(local.workflow_iam_roles)
  project  = var.project_id
  role     = each.key
  member   = google_service_account.doc_ingestion_workflow.member
}
