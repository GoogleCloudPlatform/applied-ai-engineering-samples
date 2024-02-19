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



output "performance_metrics_dataset_id" {
  description = "Performance metrics dataset id"
  value       = google_bigquery_dataset.performance_metrics_dataset.id
}

output "performance_metrics_table_id" {
  description = "Performance metrics table id"
  value       = google_bigquery_table.performance_metrics_table.id
}

output "performance_metrics_topic_id" {
  description = "Performance metrics topic ID"
  value       = google_pubsub_topic.performance_metrics_sink.id
}

output "performance_metrics_topic_name" {
  description = "Performance metrics topic name"
  value       = google_pubsub_topic.performance_metrics_sink.name
}

output "performance_metrics_bq_subscription" {
  description = "Performance metrics BQ subscription"
  value       = google_pubsub_subscription.performance_metrics_bq_subscription.id
}

