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


module "cluster" {
  source              = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gke-cluster-standard?ref=v29.0.0&depth=1"
  project_id          = var.project_id
  name                = var.cluster_config.name
  description         = var.cluster_config.description
  location            = var.region
  deletion_protection = var.deletion_protection
  release_channel     = var.cluster_config.release_channel
  min_master_version  = var.cluster_config.version
  enable_addons = {
    gcs_fuse_csi_driver            = var.cluster_config.gcs_fuse_csi_driver
    gce_persistent_disk_csi_driver = var.cluster_config.gce_persistent_disk_csi_driver
  }
  enable_features = {
    workload_identity = var.cluster_config.workload_identity
    dns = {
      provider = "CLOUD_DNS"
      scope    = "CLUSTER_SCOPE"
      domain   = "cluster.local"
    }
  }
  logging_config = {
    enable_workloads_logs          = var.cluster_config.enable_workload_logs
    enable_scheduler_logs          = var.cluster_config.enable_scheduler_logs
    enable_controller_manager_logs = var.cluster_config.enable_controller_manager_logs
    enable_enable_api_server_logs  = var.cluster_config.enable_api_server_logs
  }
  vpc_config = {
    network    = local.network_self_link
    subnetwork = local.subnet_self_link
    secondary_range_names = {
      pods     = local.pods_range_name
      services = local.services_range_name
    }
  }

}

