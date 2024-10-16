output "bigquery_dataset_id" {
  description = "The BigQuery dataset ID."
  value       = google_bigquery_dataset.dataset.dataset_id
}

output "bigquery_table_ids" {
  description = "The BigQuery tables."
  value       = [for table in google_bigquery_table.tables : table.table_id]
}

output "redis_host" {
  description = "The Memorystore Redis instance IP address."
  value       = google_redis_instance.default.host
}

output "redis_instance_name" {
  description = "The Redis instance name."
  value       = var.redis_instance_name
}

output "redis_dns_name" {
  description = "The Redis instance private DNS name."
  value       = google_dns_record_set.redis.name
}

output "compute_instance_name" {
  description = "The Compute Engine instance name."
  value       = var.compute_instance_name
}

output "compute_instance_id" {
  description = "The Compute Engine instance ID (instance number)."
  value       = google_compute_instance.dev_instance.instance_id

}
