resource "google_compute_instance" "dev_instance" {
  machine_type = "e2-standard-8"
  name         = var.compute_instance_name
  boot_disk {
    auto_delete = true
    device_name = var.compute_instance_name
    initialize_params {
      image = "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64"
      size  = 200
      type  = "pd-ssd"
    }
    mode = "READ_WRITE"
  }
  metadata = {
    startup-script = file("${path.module}/startup.sh")
  }
  network_interface {
    network    = var.vpc_network_id
    stack_type = "IPV4_ONLY"
    subnetwork = var.vpc_subnet_id
  }
  reservation_affinity {
    type = "ANY_RESERVATION"
  }
  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    provisioning_model  = "STANDARD"
  }
  service_account {
    email  = var.service_account
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = true
    enable_vtpm                 = true
  }
}
