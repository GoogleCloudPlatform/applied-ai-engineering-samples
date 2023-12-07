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


data "google_project" "project" {
  project_id = var.project_id
}

data "google_client_config" "default" {}

locals {
  pubsub_config = (
    var.prefix != ""
    ? {
      topic_name        = "${var.prefix}_${var.pubsub_config.topic_name}"
      subscription_name = "${var.prefix}_${var.pubsub_config.subscription_name}"
      schema_name       = "${var.prefix}_${var.pubsub_config.schema_name}"
    }
    : var.pubsub_config
  )

  bq_config = (
    var.prefix != ""
    ? {
      dataset_name = "${var.prefix}_${var.bq_config.dataset_name}"
      table_name   = "${var.prefix}_${var.bq_config.table_name}"
      location     = var.bq_config.location
    }
    : var.bq_config
  )
}
