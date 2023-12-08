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

locals {
  gcs_configs = {
    "${var.artifact_repository_name}" = {}
  }

  node_pool_sa = {
    name = var.node_pool_sa_name
  }

  wid_sa = {
    name = var.wid_sa_name
  }

  vpc_config = var.vpc_config

  cluster_config = {
    name        = var.cluster_name
    description = "GKE TPU training cluster"
  }

  cpu_node_pools = var.cpu_node_pools

  tpu_node_pools = var.tpu_node_pools
}

module "base_environment" {
  source         = "../../../terraform-modules/gke-aiml"
  project_id     = var.project_id
  region         = var.region
  prefix         = var.prefix
  gcs_configs    = local.gcs_configs
  node_pool_sa   = local.node_pool_sa
  wid_sa         = local.wid_sa
  vpc_config     = local.vpc_config
  cluster_config = local.cluster_config
  cpu_node_pools = local.cpu_node_pools
  tpu_node_pools = local.tpu_node_pools
}
