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


output "node_pool_sa_email" {
  description = "The email of the node pool sa"
  value       = local.node_pool_sa_email
}

output "wid_sa_email" {
  description = "The email of the workload identity sa"
  value       = local.wid_sa_email
}

output "wid_ksa" {
  description = "The name of the workload id k8s service account"
  value       = local.ksa_name
}

output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = module.cluster.name
}

output "cluster_endpoint" {
  description = "The endpoint for the GKE cluster"
  value       = module.cluster.endpoint
}

output "cluster_certificate" {
  description = "The cluster's certificate"
  sensitive   = true
  value       = module.cluster.ca_certificate
}

output "region" {
  description = "The region of the environment"
  value       = var.region
}

output "workloads_namespace" {
  description = "The default namespace for serving workloads"
  value       = var.cluster_config.workloads_namespace
}

output "gcs_buckets" {
  description = "GCS buckets created for in the environment"
  value = { for bucket in module.gcs_buckets :
    bucket.url => bucket.bucket.location
  }
}

