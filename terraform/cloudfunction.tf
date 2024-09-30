# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "source" {
    for_each        = var.cf-metadata
    type            = each.value.type
    source_dir      = each.value.source_dir
    output_path     = each.value.output_path
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "zip" {
    for_each        = var.cf-metadata
    source = data.archive_file.source[each.key].output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "src-${data.archive_file.source[each.key].output_md5}.zip"
    bucket       = google_storage_bucket.function_bucket.name

    # Dependencies are automatically inferred so these lines can be deleted
    depends_on   = [
        google_storage_bucket.function_bucket,  # declared in `storage.tf`
        data.archive_file.source
    ]
}

resource "google_cloudfunctions2_function" "rag_playground_cloud_functions" {
  for_each        = var.cf-metadata
  name            = each.value.name
  description     = each.value.description
  location        = var.region
  
  build_config {
    runtime     = each.value.runtime
    entry_point = each.value.entry_point
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.zip[each.key].name
      }
    }
  }

  service_config {
    min_instance_count               = each.value.min_instance_count
    max_instance_count               = each.value.max_instance_count
    available_memory                 = each.value.available_memory
    available_cpu                    = each.value.available_cpu
    timeout_seconds                  = each.value.timeout_seconds
    max_instance_request_concurrency = each.value.max_instance_request_concurrency
    all_traffic_on_latest_revision   = true
    service_account_email            = google_service_account.rag_sa_account.email
  }

  event_trigger {
    trigger_region = (each.value.trigger_http == "http") ? null : each.value.trigger_region
    event_type     = (each.value.trigger_http == "http") ? null : each.value.event_type
    pubsub_topic   = (each.value.trigger_http == "http") ? null : google_pubsub_topic.output.id
    retry_policy   = (each.value.trigger_http == "http") ? null : each.value.retry_policy
  }

}

resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = var.project_id
  location       = var.region
  for_each       = var.cf-metadata
  cloud_function = google_cloudfunctions2_function.rag_playground_cloud_functions[each.key].name
  role           = each.value.role
  member         = "serviceAccount:${google_service_account.rag_sa_account.email}"
  depends_on   = [google_cloudfunctions2_function.rag_playground_cloud_functions]
}