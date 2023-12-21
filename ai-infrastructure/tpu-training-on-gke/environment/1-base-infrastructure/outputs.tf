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

  tpu_types = {
    v5litepod-16  = ["4x4", 4, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4, false]
    v5litepod-32  = ["4x8", 8, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4, false]
    v5litepod-64  = ["8x8", 16, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4, false]
    v5litepod-128 = ["8x16", 32, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4, false]
    v5litepod-256 = ["16x16", 64, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4, false]
    v4-8          = ["2x2x1", 1, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, true]
    v4-16         = ["2x2x2", 2, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-32         = ["2x2x4", 4, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-64         = ["2x4x4", 8, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-128        = ["4x4x4", 16, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-256        = ["4x4x8", 32, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-512        = ["4x8x8", 64, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-1024       = ["8x8x8", 128, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-1536       = ["8x8x12", 192, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-2048       = ["8x8x16", 256, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
    v4-4096       = ["8x16x16", 512, "tpu-v4-podslice", "ct4p-hightpu-4t", 4, false]
  }
  cluster_queue_name           = "cluster-queue"
  cluster_queue_yaml_file_path = "${path.module}/templates/cluster_queue.yaml"
  _tpl_cluster_queue_yaml      = "${path.module}/templates/cluster_queue.yaml.tpl"

  node_pool_types = [for node_pool_name, node_pool in var.tpu_node_pools : node_pool.tpu_type]
  chips_per_tpu_type = { for tpu_type in distinct(local.node_pool_types) :
    tpu_type => sum([for tpu_type_name in local.node_pool_types :
  local.tpu_types[tpu_type_name][1] * local.tpu_types[tpu_type_name][4] if tpu_type_name == tpu_type]) }

  flavors = [
    for tpu_type, num_chips in local.chips_per_tpu_type :
    format("    - name: %s\n      resources:\n      - name: \"google.com/tpu\"\n        nominalQuota: %d", tpu_type, num_chips)
  ]

  cluster_queue_yaml = join("\n", concat([templatefile(local._tpl_cluster_queue_yaml, { cluster_queue_name = local.cluster_queue_name })], local.flavors))
}

resource "local_file" "cluster_queue_yaml" {
  file_permission = "0644"
  filename        = local.cluster_queue_yaml_file_path
  content         = local.cluster_queue_yaml
}

output "cluster_name" {
  value = module.base_environment.cluster_name
}

output "cluster_region" {
  value = var.region
}

output "tensorboard_id" {
  value = try(google_vertex_ai_tensorboard.tensorboard[0].id, null)
}

output "wid_ksa_name" {
  value = var.wid_sa.ksa_name
}

output "wid_ksa_namespace" {
  value = var.wid_sa.ksa_namespace
}

output "wid_gsa_email" {
  value = module.wid_service_account.email
}

output "gcs_buckets" {
  value = module.base_environment.gcs_buckets
}

output "artifact_registry_image_path" {
  description = "The URI of an Artifact Registry if created"
  value       = try(module.base_environment.artifact_registry_image_path, null)
}
