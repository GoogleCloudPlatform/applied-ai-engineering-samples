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
  bucket_configs = { for name, config in var.gcs_configs :
    "${var.prefix}-${name}" => {
      location      = config.location == "" ? var.region : config.location
      versioning    = config.versioning
      storage_class = config.storage_class
      force_destroy = !var.deletion_protection
      iam = { for role in config.iam :
        "roles/${role}" => ["serviceAccount:${local.node_pool_sa_email}", "serviceAccount:${local.wid_sa_email}"]
      }
    }
  }
}

module "gcs_buckets" {
  source        = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gcs?ref=v28.0.0&depth=1"
  for_each      = local.bucket_configs
  project_id    = var.project_id
  name          = each.key
  location      = each.value.location
  versioning    = each.value.versioning
  storage_class = each.value.storage_class
  force_destroy = each.value.force_destroy
  iam           = each.value.iam
}
