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
  node_pool_sa = {
    name = (
      var.prefix != ""
      ? "${var.prefix}-${var.node_pool_sa_name}"
      : var.node_pool_sa_name
    )
  }
  wid_sa = {
    name = (
      var.prefix != ""
      ? "${var.prefix}-${var.wid_sa_name}"
      : var.wid_sa_name
    )
  }

  gcs_configs = (
    var.prefix != ""
    ? { for name, config in var.gcs_configs :
    "${var.prefix}-${name}" => config }
    : var.gcs_configs
  )

  cluster_config = (
    var.prefix != ""
    ? merge(var.cluster_config, { name = "${var.prefix}-${var.cluster_config.name}" })
    : var.cluster_config
  )

  vpc_config = (
    var.prefix != ""
    ? merge(var.cluster_config, {
      network_name = "${var.prefix}-${var.vpc_config.network_name}"
    subnet_name = "${var.prefix}-${var.vpc_config.subnet_name}" })
    : var.vpc_config
  )

  registry_config = (
    var.artifact_registry_name != null
    ? {
      name = (
        var.prefix != ""
        ? "${var.prefix}-${var.artifact_registry_name}"
        : var.artifact_registry_name
      )
    }
    : null
  )
}

module "base_environment" {
  source              = "../../../terraform-modules/gke-aiml"
  project_id          = var.project_id
  region              = var.region
  deletion_protection = var.deletion_protection
  gcs_configs         = local.gcs_configs
  node_pool_sa        = local.node_pool_sa
  wid_sa              = local.wid_sa
  cluster_config      = local.cluster_config
  vpc_config          = local.vpc_config
  registry_config     = local.registry_config
  cpu_node_pools      = var.cpu_node_pools
  tpu_node_pools      = var.tpu_node_pools
}
