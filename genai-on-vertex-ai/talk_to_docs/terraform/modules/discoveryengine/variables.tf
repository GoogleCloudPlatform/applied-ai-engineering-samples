variable "discovery_engines" {
  type = map(object({
    industry_vertical           = optional(string, "GENERIC")
    content_config              = optional(string, "CONTENT_REQUIRED")
    location                    = optional(string, "global")
    solution_types              = optional(list(string), ["SOLUTION_TYPE_SEARCH"])
    create_advanced_site_search = optional(bool, false)
    data_store_id               = string
    search_add_ons              = optional(list(string), ["SEARCH_ADD_ON_LLM"])
    search_tier                 = optional(string, "SEARCH_TIER_ENTERPRISE")
    search_engine_id            = string
    collection_id               = optional(string, "default_collection")
    company_name                = string
  }))
  description = "The discovery engine data store and search engine to provision."
  default     = {}
}
