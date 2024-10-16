resource "google_compute_network" "vpc_network" {
  auto_create_subnetworks = false
  name                    = var.vpc_network_name
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "vpc_subnetwork" {
  ip_cidr_range            = var.vpc_subnet_cidr
  name                     = var.vpc_subnet_name
  network                  = google_compute_network.vpc_network.id
  private_ip_google_access = true
  stack_type               = "IPV4_ONLY"
}

############################################
# Cloud NAT
############################################
resource "google_compute_router" "nat_router" {
  name    = var.nat_router_name
  network = google_compute_network.vpc_network.id
}

resource "google_compute_router_nat" "nat_gateway" {
  name                               = var.nat_gateway_name
  router                             = google_compute_router.nat_router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

############################################
# Firewall Rules
############################################
resource "google_compute_firewall" "allow_iap_ingress_ssh" {
  allow {
    ports    = ["22"]
    protocol = "tcp"
  }
  direction     = "INGRESS"
  name          = "${google_compute_network.vpc_network.name}-allow-iap-ingress-ssh"
  network       = google_compute_network.vpc_network.id
  priority      = 1000
  source_ranges = ["35.235.240.0/20"]
}
