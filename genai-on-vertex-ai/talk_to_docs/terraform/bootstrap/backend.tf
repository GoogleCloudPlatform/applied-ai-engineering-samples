terraform {
  backend "gcs" {
    prefix = "bootstrap"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">=6.0.1"
    }
  }
  required_version = ">= 0.13"
}
