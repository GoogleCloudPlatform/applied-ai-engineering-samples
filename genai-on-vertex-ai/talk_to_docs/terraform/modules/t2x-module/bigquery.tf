resource "google_bigquery_dataset" "dataset" {
  dataset_id    = var.t2x_dataset_name
  location      = "US"
  friendly_name = "AI Experiment Data"
}

resource "google_bigquery_table" "tables" {
  for_each            = local.table_schemas
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = each.key
  schema              = jsonencode(each.value.fields)
  deletion_protection = false
}
