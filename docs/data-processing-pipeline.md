# Data Processing Pipeline

![Data Pipeline](./img/data_pipeline.png)

The Data Processing Pipeline is responsible for ingesting, preprocessing, and indexing your data for efficient retrieval. The pipeline is built with Apache Beam, and run on Cloud Dataflow providing scalability and fault tolerance.

**Key Stages:**

1. **Data Input and Loading:** Supports various data loaders via LangChain, allowing you to ingest data from sources like Cloud Storage or URLs. 
2. **Data Splitting:**  Utilizes LangChain splitters to divide documents into smaller chunks for embedding and indexing.
3. **Batching Documents:** Groups document chunks into mini-batches to optimize upsertion to the vector store.
4. **Upsert to Vector Store:**  Supports various vector stores via LangChain, including Vertex AI Vector Search. It manages index creation and upsertion automatically.


### Ingestion Message Schema:

The pipeline consumes messages from Pub/Sub with the following schema:

```json
{
   "input":{
      "type":"gcs",
      "config":{
         "project_name":"",
         "bucket_name":"",
         "prefix":""
      }
   },
   "data_loader":{
      "type":"document_ai",
      "config":{
         "project_id":"",
         "location":"us",
         "processor_name":"",
         "gcs_output_path":""
      }
   },
   "document_splitter":{
      "type":"recursive_char_splitter",
      "config":{
         "chunk_size": 4000
      }
   },
   "embedding_model":{
      "type":"gecko_embedding",
      "config":{
         "project_id":"",
         "location":"us",
         "model_name":"",
         "batch_size": 32
      }
   },
   "vector_store":{
      "type":"vertex_ai_vector_search",
      "config":{
         "project_id":"",
         "location":"us",
         "index_name":"",
         "batch_size": 32
      }
   }
}
```