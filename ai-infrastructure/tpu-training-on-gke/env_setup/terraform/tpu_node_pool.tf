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
  tpu_node_pool_names = [for index in range(var.num_tpu_pools) : "${var.tpu_node_pool_name_prefix}-${index}"]

  tpu_types = {
    v5litepod-16  = ["4x4", 4, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4]
    v5litepod-32  = ["4x8", 8, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4]
    v5litepod-64  = ["8x8", 16, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4]
    v5litepod-128 = ["8x16", 32, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4]
    v5litepod-256 = ["16x16", 64, "tpu-v5-lite-podslice", "ct5lp-hightpu-4t", 4]
    v4-8          = ["2x2x1", 1,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-16         = ["2x2x2", 2,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-32         = ["2x2x4", 4,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-64         = ["2x4x4", 8,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-128        = ["4x4x4", 16,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-256        = ["4x4x8", 32,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-512        = ["4x8x8", 64,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-1024       = ["8x8x8", 128,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-1536       = ["8x8x12", 192,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-2048       = ["8x8x16", 256,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
    v4-4096       = ["8x16x16", 512,"tpu-v4-podslice", "ct4p-hightpu-4t", 4]
  }
}

resource "google_container_node_pool" "tpu_node_pool" {
  for_each = toset(local.tpu_node_pool_names)

  provider           = google-beta
  project            = var.project_id
  cluster            = module.gke.cluster_id 
  name               = each.key 
  node_locations     = [var.zone]
  initial_node_count = var.enable_tpu_autoscaling ? 0 : local.tpu_types[var.tpu_type][1]

  dynamic autoscaling {
    for_each = var.enable_tpu_autoscaling ? [1] : []
    content {
      max_node_count = local.tpu_types[var.tpu_type][4] 
      location_policy      = "ANY"
    }
  }

  node_config {
    machine_type = local.tpu_types[var.tpu_type][3]
    labels = (var.num_tpu_pools > 1 ? 
              {
                MultisliceGroup=var.multislice_group_name, 
                MultisliceGroupSize=var.num_tpu_pools
              } : null)
    service_account = google_service_account.gke_service_account.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
  }

  placement_policy {
    type = "COMPACT"
    tpu_topology = local.tpu_types[var.tpu_type][0]  
  }
}
