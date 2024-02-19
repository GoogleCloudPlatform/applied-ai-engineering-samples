#  Services for performance metrics tracking 


This Terraform module creates and configures Pub/Sub and BigQuery services to facilitate the tracking of performance metrics during load testing. Load generation tools like [Locust](locust.io) can be seamlessly integrated with the metrics tracking services by publishing Pub/Sub messages conforming to [the message schema](main.tf#21) configured by the module. The content of these messages is stored and managed in BigQuery for subsequent reporting and analysis.


## Examples


```
module "locust-tracking" {
    source     = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/metrics-tracking
    project_id = "project_id"
    pubsub_config = {
       topic_name        = "locust_pubsub_sink"
       subscription_name = "locust_metrics_bq_subscription"
       schema_name       = "locust_metrics_schema"
    }
    bq_config = {
        dataset_name = "locust_metrics_dataset"
        location     = "US"
        table_name   = "locust_metrics_table"
    }
}
```


## Variables

| Name | Description | Type | Required | Default |
|---|---|---|---|---|
|[project_id](variables.tf#L26)| Project ID|`string`| &check; ||
|[deletion_protection](variables.tf#L32)|Prevent Terraform from destroying data storage Pubsub and BigQuery resources). When this field is set, a terraform destroy or terraform apply that would delete data storage resources will fail.|`string`||`true`|
|[pubsub_config](variables.tf#L39)|Pubsub configuration settings|`object({...})`|&check;||
|[bq_config](variables.tf#L49)|Bigquery configuration settings|`object({...})`|&check;||



## Outputs

| Name | Description | 
|---|---|
|[performance_metrics_dataset_id](outputs.tf#L17)|The ID of a BigQuery dataset|
|[performance_metrics_table_id](outputs.tf#L22)|The ID of a BigQuery table|
|[perforamance_metrics_topic_name](outputs.tf#L22)|The fully qualified name of the Pubsub topic|
|[performance_metrics_bq_subscription](outputs.tf#L37)|The fully qualified name of the Pubsub BigQuery subscription|


