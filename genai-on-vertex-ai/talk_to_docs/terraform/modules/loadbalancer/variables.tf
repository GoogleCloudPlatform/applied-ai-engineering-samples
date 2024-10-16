variable "project_id" {
  type        = string
  description = "The project ID."
}

variable "global_lb_domain" {
  type        = string
  description = "The global load balancer domain name."
  nullable    = true
  default     = null
}

variable "default_service" {
  type        = string
  description = "The default backend service."
}

variable "backend_services" {
  type = list(object({
    paths               = list(string)
    service             = string
    path_prefix_rewrite = optional(string, "/")
  }))
  description = "The list of load balancer backend services."
}
