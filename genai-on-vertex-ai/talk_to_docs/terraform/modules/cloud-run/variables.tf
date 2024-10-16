variable "service_name" {
  description = "The Cloud Run service name."
  type        = string
}

variable "project_id" {
  description = "The project ID."
  type        = string
}

variable "vpc_network_id" {
  type        = string
  description = "The VPC network ID."
}

variable "vpc_subnet_id" {
  type        = string
  description = "The VPC subnetwork ID."
}

variable "region" {
  type        = string
  description = "The Compute API default region."
}

variable "global_lb_domain" {
  type        = string
  description = "The global load balancer domain name."
}

variable "service_account" {
  description = "The T2X service-attached service account email address."
  type        = string
}

variable "docker_image" {
  description = "The Cloud Run service Docker image."
  type        = string
}
