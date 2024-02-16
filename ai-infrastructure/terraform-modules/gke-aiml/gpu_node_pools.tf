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

  gpu_node_pools = { for node_pool_name, node_pool in var.gpu_node_pools :
    node_pool_name => {
      taints    = node_pool.taints
      labels    = node_pool.labels
      locations = node_pool.zones
      service_account = {
        email        = local.node_pool_sa_email
        oauth_scopes = node_pool.oauth_scopes
      }
      node_config = {
        machine_type      = node_pool.machine_type
        accelerator_type  = node_pool.accelerator_type
        accelerator_count = node_pool.accelerator_count
        disk_type         = node_pool.disk_type
        disk_size_gb      = node_pool.disk_size_gb
        local_ssd_count   = 0
        spot              = false
        preemptible       = false
        image_type        = "COS_CONTAINERD"
      }
      node_count = {
        initial = node_pool.min_node_count
      }
      nodepool_config = merge(
        {
          gvnic       = node_pool.gvnic
          gcfs        = node_pool.gcfs
          gke_version = var.cluster_config.version
        },
        {
          managment = {
            auto_repair  = node_pool.auto_repair
            auto_upgrade = node_pool.auto_upgrade
          }
        },
        node_pool.min_node_count < node_pool.max_node_count ? {
          autoscaling = {
            max_node_count = node_pool.max_node_count
            min_node_count = node_pool.min_node_count
          }
        } : {}
      )
    }
  }
}

module "gpu_node_pools" {
  source          = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gke-nodepool?ref=v29.0.0&depth=1"
  project_id      = var.project_id
  for_each        = local.gpu_node_pools
  name            = each.key
  cluster_id      = module.cluster.id
  cluster_name    = module.cluster.name
  location        = var.region
  node_locations  = each.value.locations
  node_count      = each.value.node_count
  node_config     = each.value.node_config
  nodepool_config = each.value.nodepool_config
  service_account = each.value.service_account
  taints          = each.value.taints
  labels          = each.value.labels
}
