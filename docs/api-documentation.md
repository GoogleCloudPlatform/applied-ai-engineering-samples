<!-- # API Documentation

This document provides a detailed overview of the RAG Playground API, which allows you to interact with the platform's backend services. The API is built with FastAPI and offers endpoints for managing data indexing, comparing retrieval results, and more.

## Retrieval API

*   **/retrieval/index-names (GET)**

    *   **Summary:** Get Index Names
    *   **Description:** Retrieve the names of all indices from Firestore.
    *   **Returns:** A list of index names.
*   **/retrieval/compare-retrieval-results (POST)**

    *   **Summary:** Compare Retrieval Results
    *   **Description:** Compare retrieval results for different retriever-model pairs.
    *   **Request Body:**
        *   `queries (List[str])`: The queries to be used for comparison.
        *   `retriever_model_pairs (List[RetrieverModelPair])`: The retriever-model pairs to be compared.
        *   `index_name (str)`: The name of the index to be used for retrieval.
        *   `model_params (Dict[str, ModelParams])`: The parameters for the models.
        *   `is_rerank (bool)`: Whether to perform reranking.
    *   **Returns:** The comparison results.

## Index API

*   **/index/trigger-indexing-job (POST)**

    *   **Summary:** Create Indexing Job
    *   **Description:** Trigger an indexing job by publishing a message to Pub/Sub.
    *   **Request Body:**
        *   `input (Input)`: The input configuration for the indexing job.
        *   `data_loader (DataLoader)`: The data loader configuration for the indexing job.
        *   `document_splitter (DocumentSplitter)`: The document splitter configuration for the indexing job.
        *   `vector_store (VectorStore)`: The vector store configuration for the indexing job.
    *   **Returns:** A dictionary containing the status and result message.
*   **/index/get-index-request (POST)**

    *   **Summary:** Print Request
    *   **Description:** Print the index request data.
    *   **Request Body:**
        *   `input (Input)`: The input configuration for the indexing job.
        *   `data_loader (DataLoader)`: The data loader configuration for the indexing job.
        *   `document_splitter (DocumentSplitter)`: The document splitter configuration for the indexing job.
        *   `vector_store (VectorStore)`: The vector store configuration for the indexing job.
    *   **Returns:** The index request data as a dictionary.

## Data Models

The API uses several data models, including:

*   `CharacterTextSplitterConfig`
*   `CompareRetrieverRequest`
*   `CompareRetrieverResponse`
*   `DataLoader`
*   `DataLoaderConfig`
*   `DocumentSplitter`
*   `GCSInputConfig`
*   `GenericVectorStoreConfig`
*   `Input`
*   `ModelParams`
*   `PubSubMessage`
*   `RecursiveCharacterTextSplitterConfig`
*   `RetrieverModelPair`
*   `URLInputConfig`
*   `VectorStore`
*   `VertexAIVectorStoreConfig`

You can find the details of these data models in the `openapi.json` file. -->

<swagger-ui src="./api_spec/openapi.json"/>