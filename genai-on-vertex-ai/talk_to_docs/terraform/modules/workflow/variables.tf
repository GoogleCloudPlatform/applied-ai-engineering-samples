variable "project_id" {
  description = "The project ID."
  type        = string
}

variable "service_account" {
  description = "The Workflow-attached service account email address."
  type        = string
}

variable "company_name" {
  description = "The company name."
  type        = string
}

variable "data_store_id" {
  description = "The data store ID."
  type        = string
}

variable "global_lb_domain" {
  description = "The global load balancer domain name."
  type        = string
}

variable "location" {
  description = "The discoveryengine API location."
  type        = string
}

variable "search_engine_id" {
  description = "The search engine ID."
  type        = string
}
