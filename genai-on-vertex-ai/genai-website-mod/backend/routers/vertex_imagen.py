# noqa: E231

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

import os
import sys
import tomllib

from fastapi import APIRouter, HTTPException

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from models.vertex_imagen_models import (
    CaptionImageRequest,
    CaptionImageResponse,
    GenerateImagesRequest,
    GenerateImagesResponse,
    RefineImagesRequest,
    RefineImagesResponse,
)
from utils.gcs import download_file, parseStorageUrl, upload_images
from utils.imagen import caption_image, edit_image, generate_image

with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

router = APIRouter()


@router.post(path="/api/caption-image")
def captionImage(data: CaptionImageRequest) -> CaptionImageResponse:
    return caption(data=data)


def caption(data: CaptionImageRequest) -> CaptionImageResponse:
    try:
        bucket_name, blob_name = parseStorageUrl(data.image_url)
        print(f"bucket: {bucket_name} | blob: {blob_name}")

        image_bytes = download_file(
            project_id=config["global"]["project_id"],
            bucket_name=bucket_name,
            blob_name=blob_name,
        )

        results = caption_image(
            image_bytes=image_bytes, model_name=config["imagen"]["caption_model_name"]
        )
        resp = CaptionImageResponse(captions=results)
        return resp
    except Exception as e:
        print(f"[Error]generateImages: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post(path="/api/generate-images")
def generateImages(prompt: GenerateImagesRequest) -> GenerateImagesResponse:
    return generate(prompt=prompt)


def generate(prompt: GenerateImagesRequest) -> GenerateImagesResponse:
    # try:
    images = generate_image(
        prompt=prompt.prompt, model_name=config["imagen"]["generation_model_name"]
    )
    image_urls = upload_images(
        images=images,
        project_id=config["global"]["project_id"],
        bucket_name=config["blog"]["image_bucket"],
    )

    resp = GenerateImagesResponse(image_urls=image_urls)
    return resp


@router.post(path="/api/refine-image2")
def refineImage2(data: RefineImagesRequest) -> RefineImagesResponse:
    try:
        bucket_name, blob_name = parseStorageUrl(data.image_url)
        image_bytes = download_file(
            project_id=config["global"]["project_id"],
            bucket_name=bucket_name,
            blob_name=blob_name,
        )
        print(f"*** download image: {len(image_bytes)}")
        description = caption_image(image_bytes=image_bytes)

        images = generate_image(
            prompt=f"""
                Original Image:
                {description}

                Update the image to:
                {data.target_region}
                """,  # noqa: E231
            model_name=config["imagen"]["generation_model_name"],
        )

        image_urls = upload_images(
            images=images,
            project_id=config["global"]["project_id"],
            bucket_name=config["blog"]["image_bucket"],
        )

        return RefineImagesResponse(image_urls=image_urls)
    except Exception as e:
        print(f"[Error]Unable to refine image2: {e}")
        raise HTTPException(status_code=500, details=f"{e}")


@router.post(path="/api/refine-image")
def refineImage(data: RefineImagesRequest) -> RefineImagesResponse:
    try:
        bucket_name, blob_name = parseStorageUrl(data.image_url)
        image_bytes = download_file(
            project_id=config["global"]["project_id"],
            bucket_name=bucket_name,
            blob_name=blob_name,
        )
        print(f"*** download image: {len(image_bytes)}")
        images = edit_image(
            image_bytes=image_bytes,
            prompt=config["imagen"]["refine_prompt_template"].format(
                data.target_region
            ),
        )

        image_urls = upload_images(
            images=images,
            project_id=config["global"]["project_id"],
            bucket_name=config["blog"]["image_bucket"],
        )
        return RefineImagesResponse(image_urls=image_urls)

    except Exception as e:
        print(f"[Error]Unable to refine image: {e}")
        raise HTTPException(status_code=500, details=f"{e}")
