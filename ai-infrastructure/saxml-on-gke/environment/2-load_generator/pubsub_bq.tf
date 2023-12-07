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
  message_schema = "syntax = \"proto3\";\n\nmessage Metrics {\n  string test_id=1;\n  string request_type = 2;\n  string request_name=3;\n  int32 response_length=4;\n  float response_time=5;\n  string start_time=6;\n  string exception=7;\n  optional string request=8;\n  optional string response=9;\n  optional string model_name=10;\n  optional string model_method=11;\n  optional string tokenizer=12;\n  optional int32 num_output_tokens=13;\n  optional int32 num_input_tokens=14;\n  optional int32 model_response_time=15;\n}"
  table_schema   = <<EOF
[
    {
        "name": "subscription_name",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Subscription name"

    }, 
    {
        "name": "message_id",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Test ID"

    },
    {
        "name": "publish_time",
        "type": "TIMESTAMP",
        "mode": "NULLABLE",
        "description": "Test ID"

    },
    {
        "name": "attributes",
        "type": "JSON",
        "mode": "NULLABLE",
        "description": "Message attributes"

    },
    {
        "name": "test_id",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Test ID"

    },
    {
        "name": "request_type",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Request type"

    },
    {
        "name": "request_name",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Request name"

    },
    {
        "name": "response_length",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "Response length"

    },   
    {
        "name": "response_time",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "Response time in miliseconds"

    },     
    {
        "name": "start_time",
        "type": "DATETIME",
        "mode": "NULLABLE",
        "description": "Response time"

    },
    {
        "name": "exception",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Exception encounterd during request processing if any"

    },
    {
        "name": "request",
        "type": "JSON",
        "mode": "NULLABLE",
        "description": "Request body"
    },
    {
        "name": "response",
        "type": "JSON",
        "mode": "NULLABLE",
        "description": "Response body"
    },
    {
        "name": "model_name",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Model name"

    },
    {
        "name": "model_method",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Model method"
    },
    {
        "name": "tokenizer",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Tokenizer used by the model"
    },
    {
        "name": "num_output_tokens",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "Number of output tokens"
    },
    {
        "name": "num_input_tokens",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "Number of input tokens"
    },
    {
        "name": "model_response_time",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "Response time from a model server"
    }
]
EOF

  message_retention_time = "86600s"
}

resource "google_pubsub_topic" "locust_sink" {
  project    = data.google_project.project.project_id
  name       = local.pubsub_config.topic_name
  depends_on = [google_pubsub_schema.locust_metrics_schema]

  schema_settings {
    schema   = "projects/${data.google_project.project.project_id}/schemas/${local.pubsub_config.schema_name}"
    encoding = "JSON"
  }

  message_retention_duration = local.message_retention_time
}

resource "google_pubsub_schema" "locust_metrics_schema" {
  project    = data.google_project.project.project_id
  name       = local.pubsub_config.schema_name
  type       = "PROTOCOL_BUFFER"
  definition = local.message_schema
}

resource "google_bigquery_dataset" "locust_dataset" {
  project                    = data.google_project.project.project_id
  dataset_id                 = local.bq_config.dataset_name
  friendly_name              = "Locust metrics"
  description                = "Locust metrics"
  location                   = local.bq_config.location
  delete_contents_on_destroy = !var.deletion_protection

  #  access {
  #    role          = "OWNER"
  #    user_by_email = var.sa_email 
  #  }
}

resource "google_bigquery_table" "locust_metrics" {
  project             = data.google_project.project.project_id
  dataset_id          = google_bigquery_dataset.locust_dataset.dataset_id
  table_id            = local.bq_config.table_name
  schema              = local.table_schema
  deletion_protection = var.deletion_protection
}

resource "google_pubsub_subscription" "locust_bq_subscription" {
  project = data.google_project.project.project_id
  name    = local.pubsub_config.subscription_name
  topic   = google_pubsub_topic.locust_sink.name

  bigquery_config {
    table               = "${google_bigquery_table.locust_metrics.project}.${google_bigquery_table.locust_metrics.dataset_id}.${google_bigquery_table.locust_metrics.table_id}"
    use_topic_schema    = true
    drop_unknown_fields = true
    write_metadata      = true
  }

  depends_on = [google_project_iam_member.viewer, google_project_iam_member.editor]
}


resource "google_project_iam_member" "viewer" {
  project = data.google_project.project.project_id
  role    = "roles/bigquery.metadataViewer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}


resource "google_project_iam_member" "editor" {
  project = data.google_project.project.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

