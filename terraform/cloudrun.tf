# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "google_artifact_registry_repository" "rag_repo" {
  location      = var.region
  repository_id = var.repository_id
  project       = var.project_id
  format        = var.format_artifact_repo 
  description   = "A repository for testing docker via terraform"
  labels = {
    environment = "production"
  }
}

resource "docker_image" "frontend-image" {
  provider = docker.private
  name     = "${google_artifact_registry_repository.rag_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.rag_repo.name}/frontend-image:latest"
  build {
    context = "../frontend/"
    tag     = ["${google_artifact_registry_repository.rag_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.rag_repo.name}/frontend-image:latest"]
    label = {
      author : "terraform"
    }
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset("../frontend/", "**"): filesha1("../frontend/${f}")]))
  }
}

resource "docker_registry_image" "frontend" {
  provider = docker.private
  name     = docker_image.frontend-image.name
  keep_remotely = true
}

resource "docker_image" "backend-image" {
  provider = docker.private
  name     = "${google_artifact_registry_repository.rag_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.rag_repo.name}/backend-image:latest"
  build {
    context = "../backend/"
    tag     = ["${google_artifact_registry_repository.rag_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.rag_repo.name}/backend-image:latest"]
    label = {
      author : "terraform"
    }
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset("../backend/", "**"): filesha1("../backend/${f}")]))
  }
}

resource "docker_registry_image" "backend" {
  provider = docker.private
  name     = docker_image.backend-image.name
  keep_remotely = true
}


resource "random_id" "client_name" {
  byte_length = 8
}

resource "google_cloud_run_v2_service" "backend" {
  name     = "backend-image"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = docker_registry_image.backend.name
    }
    
    annotations = {
      "run.googleapis.com/client-name" = random_id.client_name.hex 
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST" 
  }
}

resource "google_cloud_run_v2_service" "frontend" {
  name     = "frontend-image"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = docker_registry_image.frontend.name
      env {
        name  = "BACKEND_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
    }
    
    annotations = {
      "run.googleapis.com/client-name" = random_id.client_name.hex 
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST" 
  }

  depends_on = [google_cloud_run_v2_service.backend]
}

resource "google_cloud_run_service_iam_member" "public-access-backend" {
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  service  = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
  depends_on = [docker_registry_image.backend]
}

resource "google_cloud_run_service_iam_member" "public-access-frontend" {
  location = google_cloud_run_v2_service.frontend.location  
  project  = google_cloud_run_v2_service.frontend.project 
  service  = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
  depends_on = [docker_registry_image.frontend]
}