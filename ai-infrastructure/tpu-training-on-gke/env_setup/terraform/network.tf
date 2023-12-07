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

resource "google_compute_network" "cluster_network" {
  name                    = var.network_name
  auto_create_subnetworks = "false"
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "cluster_subnetwork" {
  name                     = var.subnet_name
  region                   = var.region
  network                  = google_compute_network.cluster_network.self_link
  ip_cidr_range            = var.subnet_ip_range
  private_ip_google_access = true

  secondary_ip_range {
      range_name    = "ip-range-services"
      ip_cidr_range = var.services_ip_range
  }

  secondary_ip_range {
    range_name    = "ip-range-pods"
    ip_cidr_range = var.pods_ip_range
  }
}