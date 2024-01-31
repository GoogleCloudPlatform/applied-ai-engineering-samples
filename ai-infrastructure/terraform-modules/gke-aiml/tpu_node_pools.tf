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
    v5p-8         = ["2x2x1", 1, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, true]
    v5p-16        = ["2x2x2", 2, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-32        = ["2x2x4", 4, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-64        = ["2x4x4", 8, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-128       = ["4x4x4", 16, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-256       = ["4x4x8", 32, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-384       = ["4x4x12", 48, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-512       = ["4x8x8", 64, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-640       = ["4x4x20", 80, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-768       = ["4x8x12", 96, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-896       = ["4x4x28", 112, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1024      = ["8x8x8", 128, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1152      = ["4x12x12", 144, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1280      = ["4x8x20", 160, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1408      = ["4x4x44", 176, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1536      = ["8x8x12", 192, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1664      = ["4x4x52", 208, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1792      = ["4x8x28", 224, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-1920      = ["4x12x20", 240, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2048      = ["8x8x16", 256, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2176      = ["4x4x68", 272, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2304      = ["8x12x12", 288, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2432      = ["4x4x76", 304, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2560      = ["8x8x20", 320, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2688      = ["4x12x28", 336, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2816      = ["4x8x44", 352, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-2944      = ["4x4x92", 368, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3072      = ["4x12x16", 384, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3200      = ["4x20x20", 400, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3328      = ["4x8x52", 416, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3456      = ["12x12x12", 432, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3584      = ["8x8x28", 448, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3712      = ["4x4x116", 464, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3840      = ["8x12x20", 480, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-3968      = ["4x4x124", 496, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4096      = ["8x16x16", 512, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4224      = ["4x12x44", 528, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4352      = ["4x8x68", 544, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4480      = ["4x20x28", 560, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4608      = ["12x12x16", 576, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4736      = ["4x4x148", 592, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4864      = ["4x8x76", 608, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-4992      = ["4x12x52", 624, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5120      = ["8x16x20", 640, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5248      = ["4x4x164", 656, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5376      = ["8x12x28", 672, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5504      = ["4x4x172", 688, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5632      = ["8x8x44", 704, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5760      = ["12x12x20", 720, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-5888      = ["4x8x92", 736, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6016      = ["4x4x188", 752, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6144      = ["12x16x16", 768, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6272      = ["4x28x28", 784, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6400      = ["8x20x20", 800, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6528      = ["4x12x68", 816, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6656      = ["8x8x52", 832, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6784      = ["4x4x212", 848, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-6912      = ["12x12x24", 864, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7040      = ["4x20x44", 880, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7168      = ["8x16x28", 896, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7296      = ["4x12x76", 912, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7424      = ["4x8x116", 928, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7552      = ["4x4x236", 944, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7680      = ["12x16x20", 960, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7808      = ["4x4x244", 976, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-7936      = ["4x8x124", 992, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8064      = ["12x12x28", 1008, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8192      = ["16x16x16", 1024, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8320      = ["4x20x52", 1040, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8448      = ["8x12x44", 1056, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8704      = ["8x8x68", 1088, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8832      = ["4x12x92", 1104, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-8960      = ["8x20x28", 1120, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-9216      = ["12x16x24", 1152, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-9472      = ["4x8x148", 1184, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-9600      = ["12x20x20", 1200, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-9728      = ["8x8x76", 1216, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-9856      = ["4x28x44", 1232, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-9984      = ["8x12x52", 1248, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-10240     = ["16x16x20", 1280, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-10368     = ["12x12x36", 1296, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-10496     = ["4x8x164", 1312, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-10752     = ["12x16x28", 1344, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-10880     = ["4x20x68", 1360, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11008     = ["4x8x172", 1376, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11136     = ["4x12x116", 1392, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11264     = ["8x16x44", 1408, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11520     = ["12x20x24", 1440, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11648     = ["4x28x52", 1456, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11776     = ["8x8x92", 1472, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-11904     = ["4x12x124", 1488, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-12032     = ["4x8x188", 1504, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-12160     = ["4x20x76", 1520, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-12288     = ["16x16x24", 1536, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-13824     = ["12x24x24", 1728, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]
    v5p-17920     = ["16x20x28", 2240, "tpu-v5p-slice", "ct5p-hightpu-4t", 4, false]

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
      reservation_affinity = node_pool.reservation_affinity
      spot                 = node_pool.spot
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
    spot            = each.value.spot
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

  timeouts {
    create = "120m"
    update = "60m"
  }
}

