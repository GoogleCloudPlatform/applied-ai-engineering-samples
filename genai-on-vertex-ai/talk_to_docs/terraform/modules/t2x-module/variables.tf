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

variable "compute_instance_name" {
  description = "The Compute Engine instance name."
  type        = string
}

variable "service_account" {
  description = "The GCE instance service account email address."
  type        = string
}

variable "t2x_service_account_member" {
  description = "The T2X service account member."
  type        = string
}

variable "t2x_dataset_name" {
  description = "The BigQuery dataset name."
  type        = string
}

variable "redis_instance_name" {
  description = "The Redis instance name."
  type        = string
}

variable "global_lb_domain" {
  type        = string
  description = "The global load balancer domain name."
}
