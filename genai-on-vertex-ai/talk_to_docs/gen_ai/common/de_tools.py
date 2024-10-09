# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for interacting with Vertex AI Search (Discovery Engine).

This module provides functions for:
- Creating and managing Datastores.
- Creating and managing Search Engines.
- Importing and purging documents.
- Monitoring operation status.
- Interacting with Redis cache.
"""
from concurrent.futures import as_completed, Future, ThreadPoolExecutor
import json
import posixpath
from typing import Any, Callable, Iterable

from google.api_core.client_options import ClientOptions
from google.api_core.operation import Operation
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.cloud.discoveryengine_v1alpha import types
from google.cloud import storage
from google.longrunning.operations_pb2 import GetOperationRequest  # type: ignore
from google.protobuf.json_format import MessageToDict
import redis
from tqdm import tqdm

from gen_ai.common.ioc_container import Container


def sanitize(text: str) -> str:
    """Sanitize log entry text by removing newline characters.
    Satisfies GitHub CodeQL security scan.

    Args:
        text (str): The text to sanitize.

    Returns:
        str: The sanitized text.
    """
    return text.replace("\r\n", "").replace("\n", "")


def process_blob(
    blob_id: int,
    blob: storage.Blob,
    bucket: storage.Bucket,
) -> dict[str, Any] | None:
    """Process a GCS blob to extract metadata and content.

    Args:
        id (int): The ID of the blob.
        blob (storage.Blob): The GCS blob to process.
        bucket (storage.Bucket): The GCS bucket containing the blob.

    Returns:
        dict | None: The metadata JSONL data or None if the blob is not a metadata file.
    """
    Container.logger().debug(f"Processing {blob_id}: {blob.name}...")

    # Process only JSON metadata files.
    if blob.name.endswith("_metadata.json"):

        # Construct the corresponding TXT file path.
        txt_file_path = blob.name.replace("_metadata.json", ".txt")

        # Log a warning and return None if no matching TXT file.
        if not bucket.get_blob(txt_file_path):
            Container.logger().warning(f"Skipping {blob.name}. No matching TXT file found.")
            return None

        # Open the metadata blob as a stream to load the JSON data then convert it to a string.
        Container.logger().debug(f"Reading {blob.name}...")
        with blob.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        metadata_str = json.dumps(metadata)

        Container.logger().debug(f"Read {blob_id}: {blob.name} successfully.")

        # Return metadata to add to the JSONL data.
        jsonl_data = {
            "id": str(blob_id),
            "jsonData": metadata_str,
            "content": {
                "mimeType": "text/plain",
                "uri": f"gs://{posixpath.join(bucket.name, txt_file_path)}",
            },
        }
        Container.logger().debug(f"JSONL data: '{json.dumps(jsonl_data)}'")

        return jsonl_data

    # Return None if the blob is not a metadata file.
    return None


def process_result_func(results: list, result: Any, *args: tuple[int, storage.Blob]) -> None:
    """Process the result of a task function.

    Args:
        results (list): The list to store the results.
        result (Any): The result of the task function.
        args (tuple): The arguments passed to the task function.

    Returns:
        None
    """
    Container.logger().debug(f"Current results list length: {len(results)}")
    Container.logger().debug(f"Processing result: {result}")

    # Unpack the input args for traceability and append results to the collection list.
    blob_id, blob = args
    if result:
        results.append(result)
        Container.logger().debug(f"Processed {blob_id}: {blob.name} successfully.")

    return


def multithread_exec(
    task: Callable,
    iterable: Iterable,
    max_workers: int = 10,
    args: tuple = (),
    kwargs: dict | None = None,
    description: str = "Processing",
    process_result: Callable = None,
) -> list:
    """Process an iterable using a multithreaded executor.

    Args:
        task (callable): The function to execute.
        iterable (Iterable): The iterable to process.
        max_workers (int, optional): The maximum number of workers. Defaults to 10.
        args (tuple, optional): Additional arguments to pass to the task function. Defaults to ().
        kwargs (dict, optional): Additional keyword arguments to pass to the task function. Defaults to {}.
        description (str, optional): The description for the progress bar. Defaults to "Processing".
        process_result (callable, optional): A function to process the result of the task. Defaults to None.

    Returns:
        list: A list of results from the task function.
    """
    Container.logger().info(f"Starting the thread pool executor with {max_workers} workers...")
    if kwargs is None:
        kwargs = {}
    # Execute the task function with a ThreadPoolExecutor.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(task, *items, *args, **kwargs): items for items in iterable}

        # Create a progress bar for the futures.
        futures_progress: Iterable[Future] = tqdm(
            as_completed(futures),
            # total=len(futures),
            desc=description,
        )

        # Collect future results as they complete.
        result_list = []
        for future in futures_progress:

            # Get the input arguments for the future.
            future_inputs = futures[future]

            # Get the result of the future.
            try:
                result = future.result()
                Container.logger().debug(f"Future result OK: {future_inputs}")

                # Handle the result if a processing function is provided.
                process_result(result_list, result, *future_inputs)
                Container.logger().debug(f"Processing result OK: {future_inputs}")

            except Exception as e:  # pylint: disable=broad-exception-caught
                Container.logger().error(f"Error processing {future_inputs}: {e}")

    return result_list


def create_metadata_jsonl(
    project: str,
    bucket_name: str,
    source_folder: str,
    metadata_folder: str,
    dataset_name: str,
    metadata_filename: str = "metadata.jsonl",
) -> dict[str, Any]:
    """Prepares data for VAIS import.

    Creates a JSONL file from processed files and uploads it to a new GCS bucket.

    Args:
        project (str): The GCP project ID.
        bucket_name (str): The GCS bucket containing processed files.
        source_folder (str): The GCS bucket path containing processed files.
        metadata_folder (str): The GCS bucket path to store the JSONL file.
        dataset_name (str): The name to use for the dataset.
        metadata_filename (str, optional): The name of the metadata JSONL file.
        Defaults to "metadata.jsonl".

    Returns:
        dict[str, Any]: The results of the metadata JSONL file creation.
    """
    # Sanitize input values to prevent log injection.
    project = sanitize(project)
    bucket_name = sanitize(bucket_name)
    source_folder = sanitize(source_folder)
    metadata_folder = sanitize(metadata_folder)
    dataset_name = sanitize(dataset_name)
    metadata_filename = sanitize(metadata_filename)

    Container.logger().info("Preparing format for VAIS...")
    Container.logger().info(f"Project: {project}")
    Container.logger().info(f"Bucket: {bucket_name}")
    Container.logger().info(f"Source Folder: {source_folder}")
    Container.logger().info(f"Metadata Folder: {metadata_folder}")
    Container.logger().info(f"Dataset Name: {dataset_name}")

    # Create a GCS client and get the source bucket instance.
    storage_client = storage.Client(project=project)
    bucket: storage.Bucket = storage_client.bucket(bucket_name)

    # Compose the source path.
    source_path: str = posixpath.join(source_folder, dataset_name)

    # Get all files in the GCE source folder.
    # The API returns an Iterator but it's type hinted as a list to aid intellisense.
    Container.logger().info(f"Processing Documents in: gs://{bucket_name}/{source_path}...")
    all_files: list[storage.Blob] = bucket.list_blobs(prefix=source_path)

    # Process the list_pager of blobs using multithreading.
    jsonl_data = multithread_exec(
        task=process_blob,
        iterable=enumerate(all_files, start=1),
        # max_workers=50,
        args=(bucket,),
        description="Processing Metadata Files",
        process_result=process_result_func,
    )

    results = {}
    results["total_count"] = len(jsonl_data)

    Container.logger().info(f"Number of processed metadata files: {results['total_count']}")

    # Create the metadata JSONL file in the GCS output folder.
    Container.logger().info("Creating Metadata JSONL file...")
    jsonl_path = posixpath.join(metadata_folder, dataset_name, metadata_filename)
    metadata_blob = bucket.blob(jsonl_path)
    with metadata_blob.open("w", encoding="utf-8") as outfile:
        for line in jsonl_data:
            outfile.write(json.dumps(line) + "\n")

    # Construct, log, and return the metadata JSONL file URI.
    results["metadata_json_uri"] = f"gs://{posixpath.join(bucket_name, jsonl_path)}"
    Container.logger().info(f'Metadata JSONL file created at: {results["metadata_json_uri"]}')

    return results


def get_operation_dict(operation: Operation) -> dict[str, Any]:
    """Convert an Operation to a dictionary, preserving all fields.

    Args:
        operation (google.api_core.operation.Operation): The operation to convert.

    Returns:
        dict: The Operation object as a dictionary.
    """
    operation_dict = MessageToDict(
        operation,
        including_default_value_fields=True,
        preserving_proto_field_name=True,
    )
    Container.logger().info(f"Operation: {operation_dict}")
    return operation_dict


def get_datastore_client(location: str) -> discoveryengine.DataStoreServiceClient:
    """Create a DataStoreServiceClient with the specified location.

    Args:
        location (str): The location of the DataStoreServiceClient.

    Returns:
        discoveryengine.DataStoreServiceClient: The client instance.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") if location != "global" else None
    )
    return discoveryengine.DataStoreServiceClient(client_options=client_options)


def create_layout_search_datastore(
    project: str,
    location: str,
    collection: str,
    data_store_id: str,
) -> dict[str, Any]:
    """Create a Datastore using advanced chunking with the Layout parser.

    Args:
        project (str): The GCP project ID.
        location (str): The location of the DataStoreServiceClient.
        collection (str): The collection name.
        data_store_id (str): The ID of the Datastore.

    Returns:
        dict: The Datastore creation operation object as a dictionary.
    """
    # Create a client.
    client = get_datastore_client(location=location)

    # Construct the parent resource name.
    parent = client.collection_path(
        project=project,
        location=location,
        collection=collection,
    )

    Container.logger().info(f"Creating Data Store {sanitize(data_store_id)} in parent {parent}...")

    # Content config.
    content_config = discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED

    # Chunking config.
    layout_based_chunking_config = discoveryengine.DocumentProcessingConfig.ChunkingConfig.LayoutBasedChunkingConfig(
        chunk_size=500,
        include_ancestor_headings=True,
    )
    chunking_config = discoveryengine.DocumentProcessingConfig.ChunkingConfig(
        layout_based_chunking_config=layout_based_chunking_config,
    )

    # Parsing config.
    layout_parsing_config = discoveryengine.DocumentProcessingConfig.ParsingConfig.LayoutParsingConfig()
    default_parsing_config = discoveryengine.DocumentProcessingConfig.ParsingConfig(
        layout_parsing_config=layout_parsing_config,
    )

    # Document processing config.
    document_processing_config = discoveryengine.DocumentProcessingConfig(
        chunking_config=chunking_config,
        default_parsing_config=default_parsing_config,
    )

    data_store = discoveryengine.DataStore(
        display_name=data_store_id,
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config=content_config,
        document_processing_config=document_processing_config,
    )

    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=data_store_id,
    )

    # Make the request.
    operation = client.create_data_store(request=request)
    Container.logger().info(f"Operation started: {operation.operation.name}")

    # Get the operation result (a google.cloud.discoveryengine_v1alpha.types.DataStore).
    response = operation.result()
    Container.logger().info(f"Operation results: {response}")

    return get_operation_dict(operation.operation)


def get_engineservice_client(location: str) -> discoveryengine.EngineServiceClient:
    """Create an EngineServiceClient with the specified location.

    Args:
        location (str): The location of the EngineServiceClient.

    Returns:
        discoveryengine.EnginedServiceClient: The client instance.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") if location != "global" else None
    )
    return discoveryengine.EngineServiceClient(client_options=client_options)


def create_search_engine(
    project: str,
    location: str,
    collection: str,
    engine_id: str,
    data_store_id: str,
    company_name: str,
) -> dict[str, Any]:
    """Create a Search App using the specified Datastore.

    Args:
        project (str): The GCP project ID.
        location (str): The location of the EngineServiceClient.
        collection (str): The collection name.
        engine_id (str): The ID of the Search Engine.
        data_store_id (str): The ID of the Datastore.
        company_name (str): The name of the company associated with the data store documents.

    Returns:
        dict: The Search App/Engine creation operation object as a dictionary.
    """
    # Create a client.
    client = get_engineservice_client(location=location)

    # Construct the parent resource name.
    parent = client.collection_path(
        project=project,
        location=location,
        collection=collection,
    )

    Container.logger().info(f"Creating Search Engine {sanitize(engine_id)} in parent {parent}...")

    # Search engine config.
    search_tier = types.SearchTier.SEARCH_TIER_ENTERPRISE
    search_add_ons = [types.SearchAddOn.SEARCH_ADD_ON_LLM]
    search_engine_config = discoveryengine.Engine.SearchEngineConfig(
        search_tier=search_tier,
        search_add_ons=search_add_ons,
    )

    # Additional engine config.
    solution_type = types.SolutionType.SOLUTION_TYPE_SEARCH
    industry_vertical = types.IndustryVertical.GENERIC
    common_config = types.Engine.CommonConfig(company_name=company_name)

    # Initialize request argument(s).
    engine = discoveryengine.Engine(
        search_engine_config=search_engine_config,
        display_name=engine_id,
        data_store_ids=[data_store_id],
        solution_type=solution_type,
        industry_vertical=industry_vertical,
        common_config=common_config,
    )

    request = discoveryengine.CreateEngineRequest(
        parent=parent,
        engine=engine,
        engine_id=engine_id,
    )

    # Make the request.
    operation = client.create_engine(request=request)
    Container.logger().info(f"Operation started: {operation.operation.name}")

    # Get the operation result (a google.cloud.discoveryengine_v1alpha.types.Engine).
    response = operation.result()
    Container.logger().info(f"Operation results: {response}")

    return get_operation_dict(operation.operation)


def get_docservice_client(location: str) -> discoveryengine.DocumentServiceClient:
    """Create a DocumentServiceClient with the specified location.

    Args:
        location (str): The location of the DocumentServiceClient.

    Returns:
        discoveryengine.DocumentServiceClient: The client instance.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") if location != "global" else None
    )
    return discoveryengine.DocumentServiceClient(client_options=client_options)


def import_datastore_documents(
    project: str,
    location: str,
    data_store: str,
    branch: str,
    metadata_uri: str,
) -> dict[str, Any]:
    """Import documents from a GCS bucket to a branch in a Datastore.

    Args:
        project (str): The GCP project ID.
        location (str): The location of the DocumentServiceClient.
        data_store (str): The ID of the Datastore.
        branch (str): The nme of the data store branch.
        metadata_uri (str): The GCS uri to the metadata JSONL file in the source bucket.

    Returns:
        dict: The import operation object a as a dictionary.
    """
    # Create a client.
    client = get_docservice_client(location=location)

    # Construct the parent resource name.
    parent = client.branch_path(
        project=project,
        location=location,
        data_store=data_store,
        branch=branch,
    )

    Container.logger().info(f"Importing documents to parent {parent}...")
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(input_uris=[metadata_uri], data_schema="document"),
        # Options: `FULL`, `INCREMENTAL`
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    Container.logger().info(f"Metadata URI: {sanitize(metadata_uri)}")

    # Make the request.
    operation = client.import_documents(request=request)
    Container.logger().info(f"Operation started: {operation.operation.name}")

    # Don't call .result() to wait for the LRO to complete, just return the Operation object as a dictionary.
    return get_operation_dict(operation.operation)


def get_operation_status(
    location: str,
    operation_name: str,
) -> dict[str, Any]:
    """Get the status of an operation.

    Args:
        location (str): The location of the Operation.
        operation_name (str): The name of the Operation.

    Returns:
        dict: The Operation status as a dictionary.
    """
    # Create a client.
    client = get_docservice_client(location=location)

    Container.logger().info(f"Getting operation status for {operation_name}...")

    # Make the request to get the operation object.
    request = GetOperationRequest(name=operation_name)
    operation = client.get_operation(request=request)

    return get_operation_dict(operation)


def list_datastore_documents(
    project: str,
    location: str,
    data_store: str,
    branch: str,
) -> dict[Any, Any]:
    """List all documents in a Datastore.

    Args:
        project (str): The GCP project ID.
        location (str): The location of the DocumentServiceClient.
        data_store (str): The ID of the Datastore.
        branch (str): The name of the data store branch.

    Returns:
        dict:
            documents: A list of document property objects.
            total_documents: The total document count.
    """
    # Create a client.
    client = get_docservice_client(location=location)

    # Construct the parent resource name.
    parent = client.branch_path(
        project=project,
        location=location,
        data_store=data_store,
        branch=branch,
    )

    Container.logger().info(f"Listing documents from parent {parent}...")
    request = discoveryengine.ListDocumentsRequest(
        parent=parent,
    )

    # Make the request.
    list_pager = client.list_documents(request=request)

    # Construct a response with the document IDs and URIs.
    response = {
        "documents": [
            {
                "id": document.id,
                "name": document.name,
                "uri": document.content.uri,
                "metadata": document.json_data,
            }
            for document in list_pager
        ]
    }
    response["total_documents"] = len(response["documents"])

    return response


def purge_datastore_documents(
    project: str,
    location: str,
    data_store: str,
    branch: str,
    force: bool = False,
) -> dict[str, Any]:
    """Delete imported documents from a Datastore.

    Args:
        project (str): The GCP project ID.
        location (str): The location of the DocumentServiceClient.
        data_store (str): The ID of the Datastore.
        branch (str): The name of the data store branch.
        force (bool): Set to False to return expected purge without deleting anything.

    Returns:
        dict: The purge Operation object as a dictionary.
    """
    # Create a client.
    client = get_docservice_client(location=location)

    # Construct the parent resource name.
    parent = client.branch_path(
        project=project,
        location=location,
        data_store=data_store,
        branch=branch,
    )

    Container.logger().info(f"Purging documents from parent {parent}...")
    request = discoveryengine.PurgeDocumentsRequest(
        parent=parent,
        filter="*",
        force=force,
    )

    # Make the request.
    operation = client.purge_documents(request=request)
    Container.logger().info(f"Operation started: {operation.operation.name}")

    # Get the operation results.
    response = operation.result()
    Container.logger().info(f"Operation results: {response}")

    return get_operation_dict(operation.operation)


def show_redis_status(db: redis.Redis) -> dict[str, Any]:
    """Show the current status of the Redis server.

    Args:
        db (redis.Redis): The Redis client instance.

    Returns:
        dict: A dictionary containing the Redis status.
    """
    return {
        "host": db.connection_pool.connection_kwargs["host"],
        "port": db.connection_pool.connection_kwargs["port"],
        "db": db.connection_pool.connection_kwargs["db"],
        "ping": db.ping(),
        "info_memory": db.info("memory"),
        "info_keys": db.info("keyspace"),
    }


def flush_redis_cache() -> dict[str, Any]:
    """Flush the Redis cache.

    Returns:
        dict: A dictionary containing the Redis status before and after flushing.
    """
    # Get a Redis client.
    host = "redis.t2xservice.internal"
    db = redis.Redis(host=host, port=6379, db=0, decode_responses=True)

    # Initialize a dictionary to store the Redis status before and after flushing.
    redis_status = {}

    # Show db info before flushing.
    Container.logger().info("Current Redis status:")
    status_before_flush = show_redis_status(db)
    Container.logger().info(status_before_flush)
    redis_status["before_flush"] = status_before_flush

    # Flush the Redis cache.
    Container.logger().info("Evicting Redis keys...")
    db.flushall()

    # Show db info after flushing.
    Container.logger().info("Redis status after flushing:")
    status_after_flush = show_redis_status(db)
    Container.logger().info(status_after_flush)
    redis_status["after_flush"] = status_after_flush

    return redis_status
