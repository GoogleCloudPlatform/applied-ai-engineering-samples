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



module "automation_bootstrap" {
  source                   = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/bootstrap?ref=main"
  deletion_protection      = var.deletion_protection
  create_automation_sa     = var.create_automation_sa
  create_automation_bucket = var.create_automation_bucket
  enable_apis              = var.enable_apis
  project_id               = var.project_id
  automation_bucket        = var.automation_bucket
  automation_sa_name       = var.automation_sa_name
  services                 = var.services
  roles                    = var.roles
}
