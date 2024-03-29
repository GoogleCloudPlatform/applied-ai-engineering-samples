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
  manifests_path = "${path.module}/manifest-templates"
  kueue_resources = {
    for manifest in fileset(local.manifests_path, "*yaml") :
    manifest => templatefile("${local.manifests_path}/${manifest}", {
      cluster_queue_name = var.cluster_queue_name,
      local_queue_name   = var.local_queue_name,
      tpu_flavors        = var.tpu_resources,
      namespace          = var.namespace
    })
  }
}

resource "kubernetes_manifest" "kueue_manifests" {
  for_each = local.kueue_resources
  manifest = yamldecode(each.value)
  timeouts {
    create = "10m"
  }
}






