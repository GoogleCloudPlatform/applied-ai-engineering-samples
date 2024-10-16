resource "google_discovery_engine_data_store" "t2x" {
  for_each          = var.discovery_engines
  display_name      = each.value.data_store_id
  industry_vertical = each.value.industry_vertical
  content_config    = each.value.content_config
  location          = each.value.location
  data_store_id     = each.value.data_store_id

  solution_types              = each.value.solution_types
  create_advanced_site_search = each.value.create_advanced_site_search
}

resource "google_discovery_engine_search_engine" "t2x" {
  for_each       = var.discovery_engines
  display_name   = each.value.search_engine_id
  data_store_ids = [google_discovery_engine_data_store.t2x[each.key].data_store_id]

  search_engine_config {
    search_add_ons = each.value.search_add_ons
    search_tier    = each.value.search_tier
  }

  engine_id     = each.value.search_engine_id
  collection_id = each.value.collection_id
  location      = google_discovery_engine_data_store.t2x[each.key].location

  common_config {
    company_name = each.value.company_name
  }
}
