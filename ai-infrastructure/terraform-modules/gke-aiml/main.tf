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

data "google_client_config" "default" {}

locals {
  node_pool_sa_email = (
    var.node_pool_sa.email != ""
    ? var.node_pool_sa.email
    : module.service_accounts[var.node_pool_sa.name].email
  )
  wid_sa_email = (
    var.wid_sa.email != ""
    ? var.wid_sa.email
    : module.service_accounts[var.wid_sa.name].email
  )
  network_self_link   = try(var.vpc_ref.network_self_link, module.vpc.0.self_link)
  subnet_self_link    = try(var.vpc_ref.subnet_self_link, module.vpc.0.subnet_self_links["${var.region}/${var.vpc_config.subnet_name}"])
  pods_range_name     = try(var.vpc_ref.pods_ip_range_name, local.pods_ip_range_name)
  services_range_name = try(var.vpc_ref.services_ip_range_name, local.services_ip_range_name)
}
