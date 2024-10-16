output "vpc_network_id" {
  value       = google_compute_network.vpc_network.id
  description = "The VPC network ID."
}

output "vpc_subnet_id" {
  value       = google_compute_subnetwork.vpc_subnetwork.id
  description = "The VPC subnetwork ID."
}

output "vpc_subnet_cidr" {
  value       = google_compute_subnetwork.vpc_subnetwork.ip_cidr_range
  description = "The VPC subnetwork CIDR."
}

output "nat_router_id" {
  value       = google_compute_router.nat_router.id
  description = "The NAT router ID."
}

output "nat_gateway_id" {
  value       = google_compute_router_nat.nat_gateway.id
  description = "The NAT gateway ID."
}
