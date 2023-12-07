from google.cloud import pubsub_v1

# TODO(developer)
project_id = "jk-mlops-dev"
topic_id = "locust_pubsub_sink"
subscription_id = "locust_sink_bq"
bigquery_table_id = "your-project.your-dataset.your-table"

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(project_id, topic_id)
subscription_path = subscriber.subscription_path(project_id, subscription_id)

bigquery_config = pubsub_v1.types.BigQueryConfig(
    table=bigquery_table_id, write_metadata=True
)

# Wrap the subscriber in a 'with' block to automatically call close() to
# close the underlying gRPC channel when done.
with subscriber:
    subscription = subscriber.create_subscription(
        request={
            "name": subscription_path,
            "topic": topic_path,
            "bigquery_config": bigquery_config,
        }
    )

print(f"BigQuery subscription created: {subscription}.")
print(f"Table for subscription is: {bigquery_table_id}")