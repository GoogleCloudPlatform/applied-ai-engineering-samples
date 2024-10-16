output "project_id" {
  description = "The project ID."
  value       = var.project_id
}

output "vpc_network_id" {
  description = "The VPC network ID."
  value       = module.vpc.vpc_network_id
}

output "vpc_subnet_id" {
  description = "The VPC subnetwork ID."
  value       = module.vpc.vpc_subnet_id
}

output "vpc_subnet_cidr" {
  description = "The VPC subnetwork CIDR."
  value       = module.vpc.vpc_subnet_cidr
}

output "nat_router_id" {
  value       = module.vpc.nat_router_id
  description = "The NAT router ID."
}

output "nat_gateway_id" {
  value       = module.vpc.nat_gateway_id
  description = "The NAT gateway ID."
}

output "lb_ip_address" {
  description = "The load balancer IP address."
  value       = module.loadbalancer.lb_ip_address
}

output "global_lb_domain" {
  description = "The global load balancer domain name."
  value       = module.loadbalancer.global_lb_domain
}

output "cert_name" {
  description = "The Google-managed encryption certificate name."
  value       = module.loadbalancer.cert_name
}

output "bigquery_dataset_id" {
  description = "The BigQuery dataset ID."
  value       = module.t2x.bigquery_dataset_id
}

output "bigquery_table_ids" {
  description = "The BigQuery tables."
  value       = [for table_id in module.t2x.bigquery_table_ids : table_id]
}

output "t2x_service_account" {
  description = "The T2X service-attached service account email address."
  value       = module.iam.t2x_service_account_email
}

output "redis_host" {
  description = "The Memorystore Redis instance IP address."
  value       = module.t2x.redis_host
}

output "redis_instance_name" {
  description = "The Redis instance name."
  value       = module.t2x.redis_instance_name
}

output "redis_dns_name" {
  description = "The Redis instance private DNS name."
  value       = module.t2x.redis_dns_name
}

output "compute_instance_name" {
  description = "The Compute Engine instance name."
  value       = module.t2x.compute_instance_name
}

output "compute_instance_id" {
  description = "The Compute Engine instance ID (instance number)."
  value       = module.t2x.compute_instance_id
}

output "data_store_id" {
  description = "The Agent Builder data store ID."
  value       = module.discovery_engine.data_store_id
}

output "search_engine_id" {
  description = "The Agent Builder search engine ID."
  value       = module.discovery_engine.search_engine_id
}

output "docker_image_api" {
  description = "The T2X API service Docker image."
  value       = module.cloud_run_api.docker_image
}

output "custom_audience_api" {
  description = "The custom audience to authenticate calls to the T2X API Cloud Run service."
  value       = module.cloud_run_api.cloudrun_custom_audiences[0]
}

output "docker_image_ui" {
  description = "The T2X UI service Docker image."
  value       = module.cloud_run_ui.docker_image
}

output "custom_audience_ui" {
  description = "The custom audience to authenticated calls to the T2X UI Cloud Run service."
  value       = module.cloud_run_ui.cloudrun_custom_audiences[0]
}

output "health_check_url" {
  description = "The T2X API Cloud Run service health check URL."
  value       = "${module.cloud_run_api.cloudrun_custom_audiences[0]}/health"
}

output "terraform_service_account" {
  description = "The Terraform provisioning service account email address."
  value       = var.terraform_service_account
}

output "doc_ingestion_workflow_service_account" {
  description = "The document ingestion Workflow service account email address."
  value       = module.iam.workflow_service_account_email
}

output "doc_ingestion_workflow_update_time" {
  description = "The timestamp of when the workflow was last updated."
  value       = module.workflow.doc_ingestion_workflow_update_time
}

output "doc_ingestion_workflow_env_vars" {
  description = "The document ingestion workflow environment variables."
  value       = module.workflow.doc_ingestion_workflow_env_vars
}
