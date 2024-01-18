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

terraform {
  required_version = ">=1.5.1"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.6.0, < 6.0.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.6.0, < 6.0.0"
    }
  }
}

data "google_project" "project" {
  project_id = var.project_id
}

data "google_client_config" "default" {
  depends_on = [module.base_environment]
}

locals {
  node_pool_sa = (
    var.prefix != ""
    ? merge(var.node_pool_sa, { name = "${var.prefix}-${var.node_pool_sa.name}" })
    : var.node_pool_sa
  )

  wid_sa = (
    var.prefix != ""
    ? merge(var.wid_sa, { name = "${var.prefix}-${var.wid_sa.name}" })
    : var.wid_sa
  )

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
    var.create_artifact_registry == true
    ? (
      var.prefix != ""
      ? merge(var.registry_config, { name = "${var.prefix}-${var.registry_config.name}" })
      : var.registry_config
    )
    : null
  )

  tpu_node_pools = { for node_pool_name, node_pool in var.tpu_node_pools :
    node_pool_name => {
      tpu_type       = node_pool.tpu_type
      disk_size_gb   = node_pool.disk_size_gb
      zones          = node_pool.zones
      max_node_count = 1
      min_node_count = node_pool.autoscaling ? 0 : 1
    }
  }
}

module "base_environment" {
  #source              = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/gke-aiml"
  source              = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/gke-aiml?ref=saxml-on-gke-dev"
  project_id          = var.project_id
  region              = var.region
  deletion_protection = var.deletion_protection
  gcs_configs         = local.gcs_configs
  node_pool_sa        = local.node_pool_sa
  cluster_config      = local.cluster_config
  vpc_config          = local.vpc_config
  registry_config     = local.registry_config
  cpu_node_pools      = var.cpu_node_pools
  tpu_node_pools      = local.tpu_node_pools
}
