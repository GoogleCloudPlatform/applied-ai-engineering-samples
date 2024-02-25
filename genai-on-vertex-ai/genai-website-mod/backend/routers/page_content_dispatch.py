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

import json
import os
import sys
import tomllib
import uuid
from typing import Annotated, Union

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, File, HTTPException
from models.blog_edit_models import ImageResponse
from models.webcontent_edit_models import WebContentRequest, WebContentResponse
from utils.blog_utils import BlogUtil
from utils.content_cache import ContentCache
from utils.content_encoder import ContentEncoder
from utils.content_utils import ContentState, ContentUtil
from utils.gcs import ContentState, upload_file  # noqa: F811

with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

router = APIRouter()


def get_content_handler_by_url(url: str) -> Union[ContentUtil, BlogUtil]:
    if "/blog/" not in url:
        print(f"[Info]Content edit: {url}")
        return ContentUtil(
            project_id=config["global"]["project_id"],
            bucket_name=config["blog"]["blog_bucket"],
        )
    else:
        print(f"[Info]Blog edit: {url}")
        # blog_id = BlogUtil.get_blogId_from_browser_url(data.url)
        return BlogUtil(
            project_id=config["global"]["project_id"],
            bucket_name=config["blog"]["blog_bucket"],
        )


@router.post(path="/api/save-draft")
def saveDraft(data: WebContentRequest) -> WebContentResponse:
    util = get_content_handler_by_url(url=data.url)

    content_id = util.get_contentId_from_url(url=data.url)
    result = util.save_content(
        file_name=f"{content_id}.json", content=data.content, state=ContentState.DRAFT
    )
    return WebContentResponse(
        content_id=content_id,
        public_url=result,
        content=data.content,
        state=ContentState.DRAFT,
    )


@router.post(path="/api/submit-review")
def submitForReview(data: WebContentRequest) -> WebContentResponse:
    """
    Save content to review folder, and
    Delete blog in Draft folder
    """
    util = get_content_handler_by_url(url=data.url)

    content_id = util.get_contentId_from_url(url=data.url)
    result = util.copy_content(
        content_id=content_id, fromState=ContentState.DRAFT, toState=ContentState.REVIEW
    )
    return WebContentResponse(
        content_id=content_id,
        public_url=result,
        content=data.content,
        state=ContentState.REVIEW,
    )


@router.post(path="/api/publish")
def publish(data: WebContentRequest) -> Union[WebContentResponse, None]:
    """
    Save content to Production folder, and
    Delete blog in Review folder

    TODO:
    1. Refresh blog_content in blog.py
    2. Call Vertex Search Index API to reindex the new blog
    """
    util = get_content_handler_by_url(url=data.url)
    content_id = util.get_contentId_from_url(url=data.url)

    if isinstance(util, BlogUtil):
        blob_name = f"production/blog/{content_id}.json"
    elif isinstance(util, ContentUtil):
        blob_name = f"production/{content_id}.json"
    else:
        raise HTTPException(
            status_code=400, detail={"message": "Content must be web content or blog"}
        )

    content = util.fetch_content_by_id(content_id=content_id, state=ContentState.REVIEW)
    if content is not None:
        print("[INFO][DEBUG]CONTENT IS NOT NONE")
        encoder = ContentEncoder()
        result = encoder.remove_comments(content.content)
        result_text = json.dumps(result)
        result_url = upload_file(
            binary_content=result_text,
            project_id=util.project_id,
            bucket_name=util.bucket_name,
            content_type="text/plain",
            blob_name=blob_name,
        )

        util.copy_content(
            content_id=content_id,
            fromState=ContentState.PRODUCTION,
            toState=ContentState.REVIEW,
        )
        util.copy_content(
            content_id=content_id,
            fromState=ContentState.PRODUCTION,
            toState=ContentState.DRAFT,
        )
        cache = ContentCache(config=config)

        if isinstance(util, BlogUtil):
            cache.update_blog(blog_id=content_id)
        else:
            cache.update_content(content_id=content_id)

        return WebContentResponse(
            content_id=content_id,
            public_url=result_url,
            content=result_text,
            state=ContentState.PRODUCTION,
        )
    else:
        print("[INFO][DEBUG]CONTENT IS NONE")
        return None


@router.post("/api/upload-image")
def uploadFile(file: Annotated[bytes, File()]) -> ImageResponse:
    try:
        if isinstance(file, bytes):
            file_name = str(uuid.uuid4()) + ".jpg"
            contents = file
        else:
            file_name = file.filename
            contents = file.read()
        print(f"[Info]Uploading image: {file_name}")

        url = upload_file(
            binary_content=contents,
            project_id=config["global"]["project_id"],
            bucket_name=config["blog"]["image_bucket"],
            blob_name=f"images/{file_name}",
        )
        return ImageResponse(url=url)
    except Exception as e:
        print(f"[Error]upload file: {e}")
        raise HTTPException(f"{e}")


# For Review
@router.post(path="/api/save-review")
def saveReview(data: WebContentRequest) -> WebContentResponse:
    util = get_content_handler_by_url(url=data.url)

    content_id = util.get_contentId_from_url(url=data.url)
    print(f"saveReview.content_id={content_id}")
    result = util.save_content(
        file_name=f"{content_id}.json", content=data.content, state=ContentState.REVIEW
    )
    util.save_content(
        file_name=f"{content_id}.json", content=data.content, state=ContentState.DRAFT
    )
    return WebContentResponse(
        content_id=content_id,
        public_url=result,
        content=data.content,
        state=ContentState[data.state.upper()],
    )


@router.post(path="/api/fetch-content")
def fetch_content(data: WebContentRequest) -> Union[WebContentResponse, None]:
    util = get_content_handler_by_url(url=data.url)

    content_id = util.get_contentId_from_url(url=data.url)
    result = util.fetch_content_by_id(
        content_id=content_id, state=ContentState[data.state.upper()]
    )
    if result is not None:
        return WebContentResponse(
            content_id=content_id,
            public_url=result,
            content=result.content,
            state=ContentState[data.state.upper()],
        )
    else:
        return None
