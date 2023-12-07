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


# google_client_config and kubernetes provider must be explicitly specified like the following.
data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = "https://${module.gke.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke.ca_certificate)
}



module "gke" {
  source                     = "terraform-google-modules/kubernetes-engine/google"
  project_id                 = data.google_project.project.project_id
  name                       = var.cluster_name
  release_channel            = var.gke_release_channel
  kubernetes_version         = var.gke_version
  region                     = var.region
  zones                      = [var.zone]
  network                    = google_compute_network.cluster_network.name
  subnetwork                 = google_compute_subnetwork.cluster_subnetwork.name
  ip_range_pods              = google_compute_subnetwork.cluster_subnetwork.secondary_ip_range.1.range_name
  ip_range_services          = google_compute_subnetwork.cluster_subnetwork.secondary_ip_range.0.range_name
  remove_default_node_pool   = true
  http_load_balancing        = false
  network_policy             = false
  horizontal_pod_autoscaling = true
  filestore_csi_driver       = false
  create_service_account     = false 
  service_account            = google_service_account.gke_service_account.email
  grant_registry_access      = true  
  identity_namespace         = "${data.google_project.project.project_id}.svc.id.goog" 
  logging_enabled_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]

  node_pools = [
    {
      name                      = "cpu-node-pool"
      machine_type              = var.cpu_pool_machine_type 
      node_locations            = var.zone
      min_count                 = var.cpu_pool_node_count 
      max_count                 = var.cpu_pool_node_count
      local_ssd_count           = 0
      spot                      = false
      disk_size_gb              = var.cpu_pool_disk_size 
      disk_type                 = var.cpu_pool_disk_type
      image_type                = "COS_CONTAINERD"
      enable_gcfs               = false
      enable_gvnic              = false
      auto_repair               = true
      auto_upgrade              = true
      preemptible               = false
    },
  ]

  node_pools_oauth_scopes = {
    all = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ],
     
    cpu-node-pool = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
  }

  node_pools_labels = {
    all = {}

    cpu-node-pool = {
      default-node-pool = true
    }
  }

  node_pools_taints = {
    all = []

  }
}


resource "kubernetes_namespace" "tpu_namespace" {
  metadata {
    name = var.tpu_namespace
  }
}


module "tpu_workload_identity" {
  source       = "terraform-google-modules/kubernetes-engine/google//modules/workload-identity"
  project_id   = data.google_project.project.project_id
  name         = var.tpu_sa_name 
  namespace    = kubernetes_namespace.tpu_namespace.metadata[0].name 
  roles        = var.tpu_sa_roles
}


