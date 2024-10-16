data "terraform_remote_state" "main" {
  backend = "gcs"
  config = {
    bucket                      = "terraform-state-${var.project_id}"
    impersonate_service_account = var.terraform_service_account
    prefix                      = "main"
  }
  workspace = terraform.workspace
}

locals {
  config           = yamldecode(file("../../gen_ai/llm.yaml"))
  global_lb_domain = coalesce(var.global_lb_domain, try(module.loadbalancer.global_lb_domain, null))
  docker_image_api = coalesce(var.docker_image_api, try(data.terraform_remote_state.main.outputs.docker_image_api, null))
  docker_image_ui  = coalesce(var.docker_image_ui, try(data.terraform_remote_state.main.outputs.docker_image_ui, null))
}

module "vpc" {
  source           = "../modules/vpc"
  vpc_network_name = var.vpc_network_name
  vpc_subnet_name  = var.vpc_subnet_name
  vpc_subnet_cidr  = var.vpc_subnet_cidr
  nat_router_name  = var.nat_router_name
  nat_gateway_name = var.nat_gateway_name
}

module "loadbalancer" {
  source           = "../modules/loadbalancer"
  project_id       = var.project_id
  global_lb_domain = var.global_lb_domain
  default_service  = module.cloud_run_ui.cloudrun_backend_service_id
  backend_services = [
    {
      paths   = ["/${module.cloud_run_api.service_name}/*"]
      service = module.cloud_run_api.cloudrun_backend_service_id
    },
    {
      paths   = ["/${module.cloud_run_ui.service_name}/*"]
      service = module.cloud_run_ui.cloudrun_backend_service_id
    }
  ]
}

# Get the Identity-Aware Proxy (IAP) Service Agent from the google-beta provider.
resource "google_project_service_identity" "iap_sa" {
  provider = google-beta
  service  = "iap.googleapis.com"
}

module "iam" {
  source        = "../modules/iam"
  project_id    = var.project_id
  iap_sa_member = google_project_service_identity.iap_sa.member
}

module "t2x" {
  source                     = "../modules/t2x-module"
  project_id                 = var.project_id
  vpc_network_id             = module.vpc.vpc_network_id
  vpc_subnet_id              = module.vpc.vpc_subnet_id
  compute_instance_name      = local.config.terraform_instance_name
  service_account            = module.iam.t2x_service_account_email
  t2x_service_account_member = module.iam.t2x_service_account_member
  t2x_dataset_name           = local.config.dataset_name
  redis_instance_name        = local.config.terraform_redis_name
  global_lb_domain           = local.global_lb_domain
}

module "cloud_run_api" {
  source           = "../modules/cloud-run"
  service_name     = "t2x-api"
  project_id       = var.project_id
  vpc_network_id   = module.vpc.vpc_network_id
  vpc_subnet_id    = module.vpc.vpc_subnet_id
  region           = var.region
  global_lb_domain = local.global_lb_domain
  service_account  = module.iam.t2x_service_account_email
  docker_image     = local.docker_image_api
}

module "cloud_run_ui" {
  source           = "../modules/cloud-run"
  service_name     = "t2x-ui"
  project_id       = var.project_id
  vpc_network_id   = module.vpc.vpc_network_id
  vpc_subnet_id    = module.vpc.vpc_subnet_id
  region           = var.region
  global_lb_domain = local.global_lb_domain
  service_account  = module.iam.t2x_service_account_email
  docker_image     = local.docker_image_ui
}

module "discovery_engine" {
  source = "../modules/discoveryengine"
  discovery_engines = {
    t2x-default = {
      location         = local.config.vais_location
      data_store_id    = local.config.vais_data_store
      search_engine_id = local.config.vais_engine_id
      company_name     = local.config.customer_name
    }
  }
}

module "workflow" {
  source           = "../modules/workflow"
  project_id       = var.project_id
  service_account  = module.iam.workflow_service_account_email
  company_name     = local.config.customer_name
  data_store_id    = local.config.vais_data_store
  global_lb_domain = local.global_lb_domain
  location         = local.config.vais_location
  search_engine_id = local.config.vais_engine_id
}
