locals {
  config = yamldecode(file("../../gen_ai/llm.yaml"))
  # BigQuery dataset table schema.
  table_schemas = {
    "ground_truth" = {
      fields = [
        { name = "question_id", type = "STRING", mode = "REQUIRED" },
        { name = "question", type = "STRING", mode = "REQUIRED" },
        { name = "gt_answer", type = "STRING", mode = "REQUIRED" },
        { name = "gt_document_names", type = "STRING", mode = "REPEATED" },
      ]
    },
    "prediction" = {
      fields = [
        { name = "user_id", type = "STRING", mode = "REQUIRED" },
        { name = "prediction_id", type = "STRING", mode = "REQUIRED" },
        { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
        { name = "system_state_id", type = "STRING", mode = "REQUIRED" },
        { name = "session_id", type = "STRING", mode = "REQUIRED" },
        { name = "question_id", type = "STRING", mode = "REQUIRED" },
        { name = "question", type = "STRING", mode = "REQUIRED" },
        { name = "react_round_number", type = "STRING", mode = "REQUIRED" },
        { name = "response", type = "STRING", mode = "REQUIRED" },
        { name = "retrieved_documents_so_far", type = "STRING", mode = "REQUIRED" },
        { name = "post_filtered_documents_so_far", type = "STRING", mode = "REQUIRED" },
        { name = "retrieved_documents_so_far_content", type = "STRING", mode = "REQUIRED" },
        { name = "post_filtered_documents_so_far_content", type = "STRING", mode = "REQUIRED" },
        { name = "post_filtered_documents_so_far_all_metadata", type = "STRING", mode = "REQUIRED" },
        { name = "confidence_score", type = "INTEGER", mode = "REQUIRED" },
        { name = "response_type", type = "STRING", mode = "REQUIRED" },
        { name = "run_type", type = "STRING", mode = "REQUIRED" },
        { name = "time_taken_total", type = "FLOAT", mode = "REQUIRED" },
        { name = "time_taken_retrieval", type = "FLOAT", mode = "REQUIRED" },
        { name = "time_taken_llm", type = "FLOAT", mode = "REQUIRED" },
        { name = "tokens_used", type = "INTEGER", mode = "REQUIRED" },
        { name = "summaries", type = "STRING", mode = "REQUIRED" },
        { name = "relevance_score", type = "STRING", mode = "REQUIRED" },
        { name = "additional_question", type = "STRING", mode = "NULLABLE" },
        { name = "plan_and_summaries", type = "STRING", mode = "REQUIRED" },
        { name = "original_question", type = "STRING", mode = "NULLABLE" },
        { name = "client_project_id", type = "STRING", mode = "NULLABLE" },
        { name = "response_id", type = "STRING", mode = "NULLABLE" },
        { name = "context_used", type = "STRING", mode = "NULLABLE" },
      ]
    },
    "experiment" = {
      fields = [
        { name = "system_state_id", type = "STRING", mode = "REQUIRED" },
        { name = "session_id", type = "STRING", mode = "REQUIRED" },
        { name = "github_hash", type = "STRING", mode = "REQUIRED" },
        { name = "gcs_bucket_path", type = "STRING", mode = "REQUIRED" },
        { name = "pipeline_parameters", type = "STRING", mode = "REQUIRED" },
        { name = "comments", type = "STRING", mode = "NULLABLE" },
      ]
    },
    "query_evaluation" = {
      fields = [
        { name = "prediction_id", type = "STRING", mode = "REQUIRED" },
        { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
        { name = "system_state_id", type = "STRING", mode = "REQUIRED" },
        { name = "session_id", type = "STRING", mode = "REQUIRED" },
        { name = "question_id", type = "STRING", mode = "REQUIRED" },
        { name = "react_round_number", type = "STRING", mode = "REQUIRED" },
        { name = "metric_type", type = "STRING", mode = "REQUIRED" },
        { name = "metric_level", type = "STRING", mode = "REQUIRED" },
        { name = "metric_name", type = "STRING", mode = "REQUIRED" },
        { name = "metric_value", type = "FLOAT64", mode = "REQUIRED" },
        { name = "metric_confidence", type = "FLOAT64", mode = "NULLABLE" },
        { name = "metric_explanation", type = "STRING", mode = "NULLABLE" },
        { name = "run_type", type = "STRING", mode = "REQUIRED" },
        { name = "response_type", type = "STRING", mode = "REQUIRED" },
      ]
    },
    "questions" = {
      fields = [
        { name = "question_id", type = "STRING", mode = "REQUIRED" },
        { name = "question", type = "STRING", mode = "REQUIRED" },
        { name = "parent_question_id", type = "STRING", mode = "NULLABLE" },
      ]
    },
    "projects" = {
        fields = [
          { name = "project_id", type = "STRING", mode = "REQUIRED" },
          { name = "project_name", type = "STRING", mode = "REQUIRED" },
          { name = "created_on", type = "TIMESTAMP", mode = "REQUIRED" },
          { name = "updated_on", type = "TIMESTAMP", mode = "REQUIRED" },
          { name = "vertical_id", type = "STRING", mode = "REQUIRED" },
          { name = "read_only", type = "STRING", mode = "NULLABLE" },
        ]
    },
    "project_user" = {
      fields = [
        { name = "id", type = "STRING", mode = "REQUIRED" },
        { name = "project_id", type = "STRING", mode = "REQUIRED" },
        { name = "user_id", type = "STRING", mode = "REQUIRED" }
      ]
    },
    "vertical" = {
      fields = [
        { name = "vertical_id", type = "STRING", mode = "REQUIRED" },
        { name = "vertical_name", type = "STRING", mode = "REQUIRED" },
        { name = "vertical_description", type = "STRING", mode = "NULLABLE" }
      ]
    },
    "default_prompts" = {
      fields = [
        { name = "id", type = "STRING", mode = "REQUIRED" },
        { name = "vertical_id", type = "STRING", mode = "REQUIRED" },
        { name = "prompt_name", type = "STRING", mode = "REQUIRED" },
        { name = "prompt_display_name", type = "STRING", mode = "NULLABLE" },
        { name = "prompt_value", type = "STRING", mode = "NULLABLE" },
        { name = "prompt_order", type = "INTEGER", mode = "NULLABLE" }

      ]
    },
    "prompts" = {
      fields = [
        { name = "id", type = "STRING", mode = "REQUIRED" },
        { name = "vertical_id", type = "STRING", mode = "REQUIRED" },
        { name = "project_id", type = "STRING", mode = "REQUIRED" },
        { name = "prompt_name", type = "STRING", mode = "REQUIRED" },
        { name = "prompt_value", type = "STRING", mode = "NULLABLE" },
        { name = "created_on", type = "TIMESTAMP", mode = "REQUIRED" }
      ]
    }
    "lros" = {
      fields = [
        { name = "user_id", type = "STRING", mode = "REQUIRED" },
        { name = "client_project_id", type = "STRING", mode = "REQUIRED" },
        { name = "lro_id", type = "STRING", mode = "REQUIRED" },
        { name = "status", type = "STRING", mode = "REQUIRED" },
      ]
    }
    "default_questions" = {
      fields = [
        { name = "id", type = "STRING", mode = "REQUIRED" },
        { name = "client_project_id", type = "STRING", mode = "REQUIRED" },
        { name = "question", type = "STRING", mode = "NULLABLE" },
      ]
    }
  }
}
provider "google" {
  credentials = file(local.config.terraform_credentials)
  project     = local.config.bq_project_id
  region      = "us-central1"
}


resource "google_bigquery_dataset" "dataset" {
  dataset_id    = local.config.dataset_name
  project       = local.config.bq_project_id
  location      = "us-central1" # Change to your desired region
  friendly_name = "AI Experiment Data"
}


resource "google_bigquery_table" "tables" {
  for_each   = local.table_schemas
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = each.key
  schema     = jsonencode(each.value.fields)
  deletion_protection = false
}