resource "google_redis_instance" "default" {
  name               = var.redis_instance_name
  tier               = "STANDARD_HA"
  memory_size_gb     = 1
  authorized_network = var.vpc_network_id

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }
}
