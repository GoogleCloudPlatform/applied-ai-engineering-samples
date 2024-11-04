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
  node_pool_types = [for node_pool_name, node_pool in var.tpu_node_pools : node_pool.tpu_type]
  chips_per_tpu_type = { for tpu_type in distinct(local.node_pool_types) :
    tpu_type => sum([for tpu_type_name in local.node_pool_types :
  local.tpu_types[tpu_type_name][1] * local.tpu_types[tpu_type_name][4] if tpu_type_name == tpu_type]) }
}

output "node_pool_sa_email" {
  description = "The email of the node pool sa"
  value       = local.node_pool_sa_email
}

output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = module.cluster.name
}

output "cluster_endpoint" {
  description = "The endpoint of the GKE cluster"
  value       = module.cluster.endpoint
}

output "cluster_region" {
  description = "The region of the GKE cluster"
  value       = var.region
}

output "gcs_buckets" {
  description = "GCS buckets created for in the environment"
  value = { for bucket in module.gcs_buckets :
    bucket.url => bucket.bucket.location
  }
}

output "artifact_registry_id" {
  description = "The URI of an Artifact Registry if created"
  value       = try(module.registry[0].id, null)
}

output "artifact_registry_image_path" {
  description = "The URI of an Artifact Registry if created"
  value       = try(module.registry[0].image_path, null)
}

output "tpu_resources" {
  description = "Summary of TPU resources in the cluster"
  value = [for tpu_type, num_chips in local.chips_per_tpu_type :
    {
      name      = tpu_type
      num_chips = num_chips
    }
  ]
}
