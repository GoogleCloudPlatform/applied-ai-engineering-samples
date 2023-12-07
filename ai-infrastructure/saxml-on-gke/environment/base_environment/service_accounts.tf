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

  wid_sa_config = (
    !(var.wid_sa.email != "")
    ? {
      "${local.wid_sa_name}" = {
        description = var.wid_sa.description
        roles       = var.wid_sa.roles
      }
    }
    : {}
  )

  node_pool_sa_config = (
    !(var.node_pool_sa.email != "")
    ? {
      "${local.node_pool_sa_name}" = {
        description = var.node_pool_sa.description
        roles       = var.node_pool_sa.roles
      }
    }
    : {}
  )

  service_accounts = merge(local.node_pool_sa_config, local.wid_sa_config)
}


module "service_accounts" {
  source       = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account?ref=v28.0.0&depth=1"
  for_each     = local.service_accounts
  project_id   = var.project_id
  name         = each.key
  display_name = each.value.description
  iam_project_roles = {
    "${var.project_id}" = [for role in each.value.roles : "roles/${role}"]
  }
}




