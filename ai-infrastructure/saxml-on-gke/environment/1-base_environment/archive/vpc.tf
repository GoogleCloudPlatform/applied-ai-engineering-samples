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
  pods_ip_range_name     = "pods"
  services_ip_range_name = "services"
}

module "vpc" {
  source                   = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-vpc?ref=v28.0.0&depth=1"
  count                    = var.vpc_ref == null ? 1 : 0
  project_id               = var.project_id
  name                     = local.network_name
  routing_mode             = var.vpc_config.routing_mode
  create_googleapis_routes = null
  subnets = [
    {
      name          = local.subnet_name
      ip_cidr_range = var.vpc_config.subnet_ip_cidr_range
      region        = var.region
      secondary_ip_ranges = {
        "${local.pods_ip_range_name}"     = var.vpc_config.pods_ip_cidr_range
        "${local.services_ip_range_name}" = var.vpc_config.services_ip_cidr_range
      }
    }
  ]
}

module "nat" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-cloudnat?ref=v28.0.0&depth=1"
  count          = var.vpc_ref == null ? 1 : 0
  project_id     = var.project_id
  region         = var.region
  name           = var.vpc_config.nat_router_name
  router_create  = true
  router_network = module.vpc.0.name
}


