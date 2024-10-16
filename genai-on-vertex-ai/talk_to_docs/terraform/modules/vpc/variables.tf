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
  description = "The VPC subnet CIDR."
}

variable "nat_router_name" {
  type        = string
  description = "The NAT router name."
}

variable "nat_gateway_name" {
  type        = string
  description = "The NAT gateway name."
}
