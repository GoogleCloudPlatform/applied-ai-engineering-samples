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
  jobset_manifests = "https://github.com/kubernetes-sigs/jobset/releases/download/${var.jobset_version}/manifests.yaml"
  kueue_manifests  = "https://github.com/kubernetes-sigs/kueue/releases/download/${var.kueue_version}/manifests.yaml"

  cluster_queue_manifest = templatefile("${path.module}/manifest-templates/cluster_queue.yaml",
  { cluster_queue_name = var.cluster_queue_name, tpu_flavors = var.tpu_resources })

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

resource "terraform_data" "install_jobset" {
  triggers_replace = [
    var.jobset_version
  ]

  provisioner "local-exec" {
    command = "kubectl apply --server-side -f ${local.jobset_manifests}"
  }
}

resource "terraform_data" "install_kueue" {
  triggers_replace = [
    var.jobset_version
  ]

  provisioner "local-exec" {
    command = "kubectl apply --server-side -f ${local.kueue_manifests}"
  }
}

resource "time_sleep" "wait_for_kueue" {
  depends_on = [terraform_data.install_kueue]

  create_duration = "60s"
}

resource "local_file" "test" {
  for_each        = local.kueue_resources
  file_permission = "0644"
  filename        = "test/${each.key}"
  content         = each.value
}





