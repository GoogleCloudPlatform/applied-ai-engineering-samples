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


output "locust_dataset_id" {
  description = "Locust metrics dataset id"
  value       = google_bigquery_dataset.locust_dataset.id
}

output "locust_metrics_table_id" {
  description = "Locust metrics table id"
  value       = google_bigquery_table.locust_metrics.id
}

output "locust_metrics_topic_id" {
  description = "Locust metrics topic ID"
  value       = google_pubsub_topic.locust_sink.id
}

output "locust_metrics_topic_name" {
  description = "Locust metrics topic name"
  value       = google_pubsub_topic.locust_sink.name
}

output "locust_metrics_bq_subscription" {
  description = "Locust metrics BQ subscription"
  value       = google_pubsub_subscription.locust_bq_subscription.id
}


