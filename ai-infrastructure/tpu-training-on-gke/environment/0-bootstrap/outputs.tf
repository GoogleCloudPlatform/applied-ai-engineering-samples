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


output "automation_bucket_name" {
  description = "GCS bucket where Terraform automation artifacts are managed"
  value       = module.automation_bootstrap.automation_bucket_name
}

output "automation_sa_email" {
  description = "The email of the automation service account"
  value       = module.automation_bootstrap.automation_sa_email
}
