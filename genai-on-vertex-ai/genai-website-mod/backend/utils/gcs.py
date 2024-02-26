# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
from enum import Enum
from typing import Any

import requests
from google.cloud import storage


class ContentState(Enum):
    PRODUCTION = "PRODUCTION"
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"


def parseStorageUrl(url: str) -> tuple[str, str]:
    if url.startswith("https://"):
        gcs_url = url.replace("https://storage.googleapis.com/", "")
        bucket = gcs_url.split("/")[0]
        blob = gcs_url.replace(f"{bucket}/", "")
    elif url.startswith("gs://"):
        # gs://<bucket>/draft/1.html
        bucket = url.replace("gs://", "").split("/")[0]
        blob = url.replace(f"gs://{bucket}/", "")  # noqa: E231
    return bucket, blob


def upload_images(images: Any, project_id: str, bucket_name: str) -> list[str]:
    image_urls = []
    for index in range(0, len(images.images)):
        url = upload_file(
            binary_content=images[index]._image_bytes,
            project_id=project_id,
            blob_name=f"images/imagen-{random.randrange(start=1, stop=10000000)}.png",
            bucket_name=bucket_name.lower(),
        )
        image_urls.append(url)
    return image_urls


def copy_file(
    project_id: str,
    source_bucket: str,
    source_blob: str,
    new_bucket: str,
    new_blob: str,
) -> str:
    storage_client = storage.Client(project=project_id)

    source_bucket_client = storage_client.bucket(source_bucket)
    source_blob_client = source_bucket_client.blob(source_blob)
    destination_bucket = storage_client.bucket(new_bucket)

    blob_copy = source_bucket_client.copy_blob(
        source_blob_client, destination_bucket, new_blob
    )

    return blob_copy.public_url


def move_file(
    project_id: str,
    source_bucket: str,
    source_blob: str,
    new_bucket: str,
    new_blob: str,
) -> str:
    storage_client = storage.Client(project=project_id)

    source_bucket_client = storage_client.bucket(source_bucket)
    source_blob_client = source_bucket_client.blob(source_blob)
    destination_bucket = storage_client.bucket(new_bucket)

    # destination_generation_match_precondition = 0

    blob_copy = source_bucket_client.copy_blob(
        source_blob_client, destination_bucket, new_blob
    )
    source_blob_client.delete()

    return blob_copy.public_url


def upload_file(
    binary_content: Any,
    project_id: str,
    bucket_name: str,
    blob_name: str,
    content_type="image/png",
) -> str:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name.lower())
    blob = bucket.blob(blob_name.lower())
    blob.upload_from_string(binary_content, content_type=content_type)

    return blob.public_url


def download_file_from_url(url: str) -> bytes:
    try:
        response = requests.get(url)
        print("[Info]Download file from url")
        return response.content
    except Exception as e:
        print(f"[Error]Unable to download file: {e}")
        return bytes()


def download_file(project_id: str, bucket_name: str, blob_name: str) -> bytes:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if blob.exists():
        print("[Info]Download file")
        return blob.download_as_bytes()
    else:
        print(f"[Warning]{blob_name} does not exists")
        return bytes()


def list_files(project_id: str, bucket_name: str, file_prefix: str = "") -> list[dict]:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    if file_prefix is not None and file_prefix != "":
        blobs = bucket.list_blobs(prefix=file_prefix)
    else:
        blobs = bucket.list_blobs()
    return [
        {
            "name": "gs://" + bucket_name + "/" + blob.name,
            "storage_class": blob.storage_class,
            "public_url": blob.public_url,
        }
        for blob in blobs
        if not blob.name.endswith("/")
    ]


def delete_file(project_id: str, bucket_name: str, blob_name: str) -> None:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
