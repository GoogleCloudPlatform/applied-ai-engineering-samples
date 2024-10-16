output "lb_ip_address" {
  description = "The load balancer IP address."
  value       = google_compute_global_address.t2x_lb_global_address.address
}

output "global_lb_domain" {
  description = "The global load balancer domain name."
  value       = local.t2x_lb_domain
}

output "cert_name" {
  description = "The Google-managed encryption certificate name."
  value       = google_compute_managed_ssl_certificate.cert.name
}
