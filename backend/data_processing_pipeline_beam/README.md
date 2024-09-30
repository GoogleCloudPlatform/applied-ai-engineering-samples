# Large Scale RAG Data Processing on Dataflow - Template

Dataflow Template for large scale RAG document processing

## 1. Setup the custom dataflow flex template image

1. Export required env variables
    ```bash
    export PROJECT_ID=$(gcloud config get-value project)
    export TEMPLATE_IMAGE="gcr.io/$PROJECT_ID/dataflow/rag_playground_pipeline:latest"
    ```

2. Build Dataflow Flex Template using Cloud Build
    ```bash
    gcloud builds submit --tag $TEMPLATE_IMAGE .
    ```
---

## 2. Stage and build the dataflow flex Template

1. Export required env variables
    ```bash
    export TEMPLATE_PATH="gs://${PROJECT_ID}/templates/rag_playground_pipeline_metadata.json"
    ```

2. Build and upload the template to GCS
    ```bash
    gcloud beta dataflow flex-template build $TEMPLATE_PATH \
        --image "$TEMPLATE_IMAGE" \
        --sdk-language "PYTHON" \
        --metadata-file "rag_playground_pipeline_metadata.json"
    ```
---
## 3. Run the dataflow job

1. Export the required env variables

    ```bash
    export PROJECT_ID=$(gcloud config get-value project)
    export REGION=us-central1
    export JOB_NAME=rag-playground-dataflow-pipeline-$(date +%Y%m%H%M$S)

    export INPUT_PUBSUB_SUBSCRIPTION=projects/{PROJECT_ID}/subscriptions/document-processing-input-sub
    export OUTPUT_PUBSUB_TOPIC=projects/{PROJECT_ID}/topics/document-processing-output
    ```

2. Create and run the job from the Flex Template
    ```bash
    gcloud beta dataflow flex-template run ${JOB_NAME} \
        --region=$REGION \
        --template-file-gcs-location ${TEMPLATE_LOC} \
        --parameters "input_subscription=${INPUT_PUBSUB_SUBSCRIPTION},output_topic=${OUTPUT_PUBSUB_TOPIC}"
    ```

3. Once the workers are ready to accept requests - you can publish the following message format to the input Pub/Sub subscription
    ```json
    {
        "input": {
            "type": "gcs",
            "config": {
                "project_name": "PROJECT_ID",
                "bucket_name": "BUCKET_ID",
                "prefix": "world-bank",
            },
        },
        "data_loader": {
            "type": "document_ai",
            "config": {
                "project_id": "PROJECT_ID",
                "location": "us",
                "processor_name": "projects/PROJECT_NUMBER/locations/us/processors/PROCESSOR_ID",
                "gcs_output_path": "gs://BUCKET_NAME/output",
            },
        },
        "document_splitter": {
            "type": "recursive_character",
            "config": {"chunk_size": 1000, "chunk_overlap": 200},
        },
        "vector_store": {
            "type": "vertex_ai",
            "config": {
                "project_id": "PROJECT_ID",
                "region": "us-central1",
                "index_id": "INDEX_ID",
                "endpoint_id": "ENDPOINT_ID",
                "embedding_model": "text-embedding-004",
                "index_name": "UNIQUE_INDEX_NAME",
            },
        },
    }
    ```

    or with URL Inputs like 

    ```json
    {
    "input": {
        "type": "url",
        "config": {
            "url": "https://en.wikipedia.org/wiki/Google"
        },
    },
    "data_loader": {
        "type": "document_ai",
        "config": {
            "project_id": "PROJECT_ID",
            "location": "us",
            "processor_name": "projects/PROJECT_NUMBER/locations/us/processors/PROCESSOR_ID",
            "gcs_output_path": "gs://BUCKET_NAME/output",
        },
    },
    "document_splitter": {
        "type": "recursive_character",
        "config": {"chunk_size": 1000, "chunk_overlap": 200},
    },
    "vector_store": {
        "type": "vertex_ai",
        "config": {
            "project_id": "PROJECT_ID",
            "region": "us-central1",
            "index_id": "INDEX_ID",
            "endpoint_id": "ENDPOINT_ID",
            "embedding_model": "text-embedding-004",
            "index_name": "UNIQUE_INDEX_NAME",
            },
        },
    }
    ```