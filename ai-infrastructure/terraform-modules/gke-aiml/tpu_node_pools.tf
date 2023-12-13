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
    v5litepod-1   = ["1x1", 1, "tpu-v5-lite-podslice", "ct5lp-hightpu-1t", 1, true]
    v5litepod-4   = ["2x2", 1, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4, true]
    v5litepod-8   = ["2x4", 1, "tpu-v5-lite-podslice", "ct5lp-hightpu-8t", 8, true]
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

  tpu_node_pools = { for node_pool_name, node_pool in var.tpu_node_pools :
    node_pool_name => {
      machine_type   = local.tpu_types[node_pool.tpu_type][3]
      disk_type      = node_pool.disk_type
      disk_size_gb   = node_pool.disk_size_gb
      tpu_topology   = local.tpu_types[node_pool.tpu_type][0]
      zones          = node_pool.zones
      multihost      = local.tpu_types[node_pool.tpu_type][5]
      min_node_count = node_pool.min_node_count
      max_node_count = node_pool.max_node_count
      node_count     = local.tpu_types[node_pool.tpu_type][1]
      gvnic          = node_pool.gvnic
      gke_version    = var.cluster_config.version
      initial_node_count = (
        node_pool.min_node_count < node_pool.max_node_count
        ? 0
        : local.tpu_types[node_pool.tpu_type][5]
        ? node_pool.max_node_count
        : local.tpu_types[node_pool.tpu_type][1]
      )
      autoscaling          = node_pool.min_node_count < node_pool.max_node_count
      gvnic                = node_pool.gvnic
      taints               = node_pool.taints
      labels               = node_pool.labels
      oauth_scopes         = node_pool.oauth_scopes
      reservation_affinity = null
    }
  }
}



resource "google_container_node_pool" "tpu_node_pools" {
  for_each = local.tpu_node_pools

  provider           = google-beta
  project            = var.project_id
  cluster            = module.cluster.id
  name               = each.key
  node_locations     = each.value.zones
  initial_node_count = each.value.initial_node_count

  dynamic "autoscaling" {
    for_each = each.value.autoscaling && !each.value.multihost ? [""] : []
    content {
      total_min_node_count = each.value.min_node_count
      total_max_node_count = each.value.max_node_count
      location_policy      = "ANY"
    }
  }

  dynamic "autoscaling" {
    for_each = each.value.autoscaling && each.value.multihost ? [""] : []
    content {
      max_node_count  = each.value.node_count
      location_policy = "ANY"
    }
  }

  node_config {
    machine_type    = each.value.machine_type
    service_account = local.node_pool_sa_email
    disk_type       = each.value.disk_type
    disk_size_gb    = each.value.disk_size_gb
    oauth_scopes    = each.value.oauth_scopes
    gvnic {
      enabled = each.value.gvnic
    }
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    dynamic "taint" {
      for_each = each.value.taints
      content {
        key    = taint.key
        value  = taint.value.key
        effect = taint.value.effect
      }
    }

    labels = each.value.labels

    dynamic "reservation_affinity" {
      for_each = each.value.reservation_affinity != null ? [""] : []
      content {
        consume_reservation_type = each.value.reservation_affinity.consume_reservation_type
        key                      = each.value.reservation_affinity.key
        values                   = each.value.reservation_affinity.values
      }
    }
  }

  dynamic "placement_policy" {
    for_each = each.value.multihost ? [] : [1]
    content {
      type         = "COMPACT"
      tpu_topology = each.value.tpu_topology
    }
  }
}

