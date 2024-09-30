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

resource "google_storage_bucket" "bucket" {
  name     = var.vertex_ai_bucket_name
  location = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "empty_data" {
  name   = "contents/empty_data.json"
  bucket = google_storage_bucket.bucket.name
  content = jsonencode({
    "id": "00000000-0000-0000-0000-000000000000",
    "embedding": [for i in range(768) : 0.0]
  })
}

resource "google_vertex_ai_index" "custom_index" {
  region       = var.region
  display_name = var.vertex_ai_index_name
  description  = "Custom index with specified configurations"
  metadata {
    contents_delta_uri = "gs://${google_storage_bucket.bucket.name}/contents"
    config {
      dimensions = 768
      approximate_neighbors_count = 150
      shard_size = "SHARD_SIZE_LARGE"
      distance_measure_type = "DOT_PRODUCT_DISTANCE"
      feature_norm_type = "NONE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count = 500
          leaf_nodes_to_search_percent = 5
        }
      }
    }
  }
  index_update_method = "STREAM_UPDATE"
}

resource "google_vertex_ai_index_endpoint" "index_endpoint" {
  display_name = var.vertex_ai_index_endpoint_name
  description  = "Endpoint for custom index"
  region       = var.region
  public_endpoint_enabled = false
}

resource "google_vertex_ai_index_endpoint_deployed_index" "deployed_index" {
  index_endpoint = google_vertex_ai_index_endpoint.index_endpoint.id
  deployed_index_id = var.vertex_ai_deployed_index_id
  display_name = "Deployed Custom Index"
  index        = google_vertex_ai_index.custom_index.id

  dedicated_resources {
    machine_spec {
      machine_type = "n1-standard-32"
    }
    min_replica_count = 1
    max_replica_count = 1
  }
}