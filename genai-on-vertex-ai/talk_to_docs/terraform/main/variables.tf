variable "project_id" {
  description = "The project ID."
  type        = string
}

variable "terraform_service_account" {
  type        = string
  description = "The Terraform provisioning service account email address."
}

variable "region" {
  type        = string
  description = "The Compute API deafult region."
  default     = "us-central1"
}

variable "zone" {
  type        = string
  description = "The Compute API default zone."
  default     = "us-central1-a"
}

variable "vpc_network_name" {
  type        = string
  description = "The VPC network name."
}

variable "vpc_subnet_name" {
  type        = string
  description = "The VPC subnetwork name."
}

variable "vpc_subnet_cidr" {
  type        = string
  description = "The VPC subnetwork CIDR."
}

variable "nat_router_name" {
  type        = string
  description = "The NAT router name."
}

variable "nat_gateway_name" {
  type        = string
  description = "The NAT gateway name."
}

variable "global_lb_domain" {
  description = "The global load balancer domain name."
  type        = string
  default     = null
  nullable    = true
}

variable "docker_image_api" {
  description = "The T2X API Cloud Run service Docker image."
  type        = string
  nullable    = true
  default     = null
}

variable "docker_image_ui" {
  description = "The T2X UI Cloud Run service Docker image."
  type        = string
  nullable    = true
  default     = null
}
