output "t2x_service_account_email" {
  description = "The T2X service-attached service account email address."
  value       = google_service_account.t2x_service_account.email
}

output "t2x_service_account_member" {
  description = "The T2X service account member."
  value       = google_service_account.t2x_service_account.member
}

output "workflow_service_account_email" {
  description = "The Workflow service account email address."
  value       = google_service_account.doc_ingestion_workflow.email
}