resource "google_dns_managed_zone" "redis_private_zone" {
  name        = "redis-private-zone"
  dns_name    = "t2xservice.internal."
  description = "Private DNS zone to allow hostname connections to the T2X Redis instance."
  visibility  = "private"
  private_visibility_config {
    networks {
      network_url = var.vpc_network_id
    }
  }
}

resource "google_dns_record_set" "redis" {
  name         = "redis.t2xservice.internal."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.redis_private_zone.name
  rrdatas      = [google_redis_instance.default.host]
  depends_on   = [google_redis_instance.default]
}

resource "google_dns_managed_zone_iam_member" "dns_reader" {
  managed_zone = google_dns_managed_zone.redis_private_zone.name
  role         = "roles/dns.reader"
  member       = var.t2x_service_account_member
}
