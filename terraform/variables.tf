# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Default resource location"
  type        = string
}

variable "resource_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "backend_staging_bucket" {
  description = "GCS bucket for Terraform state"
  type        = string
}

variable "tf_state_prefix" {
  description = "Prefix for Terraform state files"
  type        = string
}

# --- Artifact Repository ---
variable "repository_id" {
  description = "ID of Artifact Repository"
  type        = string
}

variable "format_artifact_repo" {
  description = "Format of artifacts in Artifact Repository"
  type        = string
}

# --- Service Accounts ---
variable "rag_playground_sa_id" {
  description = "ID for the RAG Playground service account"
  type        = string
}

variable "rag_playground_sa_display_name" {
  description = "Display name for the RAG Playground service account"
  type        = string
  default     = "Service Account For RAG Playground"
}

variable "rag_workflow_sa_id" {
  description = "ID for the RAG Workflow service account"
  type        = string
  default     = "rag-workflow-sa"
}

variable "rag_workflow_sa_display_name" {
  description = "Display name for the RAG Workflow service account"
  type        = string
  default     = "RAG Workflow Service Account"
}
# --- Workflow Orchestrator ---
variable "workflow_name" {
  description = "Name of the Cloud Workflow Orchestrator"
  type        = string
  default     = "rag-playground-backend-workflow"
}
# --- Pub/Sub ---
variable "output_topic_name" {
  description = "Name of the output Pub/Sub topic"
  type        = string
  default     = "document-processing-output"
}

variable "input_topic_name" {
  description = "Name of the input Pub/Sub topic"
  type        = string
  default     = "document-processing-input"
}

variable "input_topic_subscription_name" {
  description = "Name of the subscription for input Pub/Sub topic"
  type        = string
  default     = "document-processing-input-subscription"
}


variable "dataflow_job_name" {
    description = "name of the dataflow job"
    type = string
    default = "dataflow-flextemplates-job" 
}

variable "dataflow_metadata_filename" {
    description = "Filename for the Dataflow metadata JSON"
    type = string
    default = "rag_playground_pipeline_metadata.json"
}
# --- Firestore ---
variable "firestore_database_name" {
  description = "Name of the Firestore database"
  type        = string
  default     = "(default)"
}

variable "firestore_database_type" {
  description = "Type of the Firestore database"
  type        = string
  default     = "FIRESTORE_NATIVE"
}

variable "firestore_concurrency_mode" {
  description = "Concurrency mode for the Firestore database"
  type        = string
  default     = "OPTIMISTIC"
}

variable "firestore_app_engine_integration_mode" {
  description = "App Engine integration mode for the Firestore database"
  type        = string
  default     = "DISABLED"
}

variable "firestore_point_in_time_recovery_enablement" {
  description = "Point-in-time recovery enablement for the Firestore database"
  type        = string
  default     = "POINT_IN_TIME_RECOVERY_ENABLED"
}

variable "firestore_delete_protection_state" {
  description = "Delete protection state for the Firestore database"
  type        = string
  default     = "DELETE_PROTECTION_DISABLED"
}

variable "firestore_deletion_policy" {
  description = "Deletion policy for the Firestore database"
  type        = string
  default     = "DELETE"
}

variable "firebase_config_file_path" {
  description = "Path to the firebase config JSON file"
  type        = string
  default     = "./firebase_config.json"
}

variable "firestore_collection_name" {
  description = "Name of the Firestore collection"
  type        = string
  default     = "config"
}

variable "firestore_document_id" {
  description = "ID of the Firestore document"
  type        = string
  default     = "app_config"
}

# --- Vertex AI Vector Search ---
variable "vertex_ai_bucket_name" {
  description = "Name of the bucket for Vertex AI Vector Search"
  type        = string
}

variable "vertex_ai_index_name" {
  description = "Name of the Vertex AI Vector Search index"
  type        = string
}

variable "vertex_ai_index_endpoint_name" {
  description = "Name of the Vertex AI Vector Search index endpoint"
  type        = string
}

variable "vertex_ai_deployed_index_id" {
  description = "ID of the deployed Vertex AI Vector Search index"
  type        = string
}

variable "document_ai_processor_display_name" {
  description = "Display name for the Document AI processor"
  type        = string
  default     = "layout-parser-processor"
}

variable "document_ai_processor_type" {
  description = "Type of the Document AI processor"
  type        = string
  default     = "LAYOUT_PARSER_PROCESSOR"
}

# --- Cloud Functions ---
variable "cf-metadata" {
  description = "Configurations of Cloud Functions"
  type = map(object({
    type        = string
    source_dir  = string
    output_path = string
    name        = string
    description = string
    runtime     = string
    entry_point = string
    min_instance_count = number
    max_instance_count = number
    available_memory   = string
    timeout_seconds    = number
    max_instance_request_concurrency = number
    available_cpu = string
    trigger_region = string
    event_type     = string
    retry_policy   = string
    trigger_http = string
    role        = string
  }))
  default = {
    source_ans_gen_service = {
      type   = "zip"
      source_dir = "../backend/answer_generation_service"
      output_path  = "./tmp/answer_generation_service_function.zip"
      name   = "answer_generation_service"
      description = "answer generation service"
      runtime     = "python312"
      trigger_http = "http"
      entry_point  = "execute_rag_query"     
      min_instance_count = 10
      max_instance_count = 100
      available_memory   = "2Gi"
      timeout_seconds    = 60
      max_instance_request_concurrency = 1
      available_cpu = "2"
      trigger_region = ""
      event_type     = ""
      retry_policy   = ""
      role         = "roles/cloudfunctions.invoker"
    }
    source_rp_eval_service = {
      type         = "zip"
      source_dir   = "../backend/answer_evaluation_service"
      output_path  = "./tmp/eval_service_function.zip"
      name         = "answer_evaluation_service"
      description  = "answer evaluation service"
      runtime     = "python312"
      trigger_http = "http"
      entry_point  = "evaluate_rag_answer"
      min_instance_count = 10
      max_instance_count = 100
      available_memory   = "2Gi"
      timeout_seconds    = 60
      max_instance_request_concurrency = 1
      available_cpu = "2"
      trigger_region = ""
      event_type     = ""
      retry_policy   = ""
      role         = "roles/cloudfunctions.invoker"
    }
    source_pubsub_fs_trigger = {
      type   = "zip"
      source_dir = "../backend/pubsub_trigger_service"
      output_path  = "./tmp/pubsub_fs_trigger_function.zip"
      name   = "pubsub-fs-trigger"
      description = "pubsub fs trigger function"
      runtime     = "python312"
      trigger_http = "pub-sub"
      entry_point  = "pubsub_to_firestore"     
      min_instance_count = 0
      max_instance_count = 10
      available_memory   = "256M"
      timeout_seconds    = 60
      max_instance_request_concurrency = 1
      available_cpu = "1"
      trigger_region = "us-central1"
      event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
      retry_policy   = "RETRY_POLICY_RETRY"
      role         = "roles/cloudfunctions.invoker"
      replacement_text = "fn_url_pub_sub"
    }
  }
}