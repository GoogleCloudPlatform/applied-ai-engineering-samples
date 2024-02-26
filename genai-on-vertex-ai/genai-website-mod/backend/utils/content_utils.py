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
from typing import Optional, Union

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.content_encoder import ContentEncoder
from utils.gcs import (
    ContentState,
    copy_file,
    delete_file,
    download_file,
    list_files,
    move_file,
    upload_file,
)


class WebpageContent:
    blog_id: Optional[str | None] = None
    content: str = ""

    def __init__(self, url: str, content: str = ""):
        self.url = url
        self.__parseStorageUrl(url)
        self.content = content if content is not None and content != "" else ""

    def __parseStorageUrl(self, url: str) -> None:
        self.environment_name = url.split("/")[-2]

        try:
            if url.startswith("https://storage.googleapis.com/"):
                # https://storage.googleapis.com/website-mod-imagen-outputs/production/test_content.json
                gcs_url = url.replace("https://storage.googleapis.com/", "")
                print(f"***gcs_url={gcs_url}")
                gcs_urls = gcs_url.split("/")
                # self.project_id = gcs_url.split("/")[0]
                self.bucket = gcs_urls[0]
                print(f"**self.bucket={self.bucket}")
                self.content_id = gcs_urls[-1][0 : gcs_urls[-1].index(".")]
                print(f"**self.content_id={self.content_id}")
                self.blob = "/".join(
                    gcs_urls[1:]
                )  # gcs_url.replace(self.bucket + "/", "")
                print(f"**self.blob={self.blob}")
                state_str = self.blob.split("/")[0]
                print(f"**self.state_str={state_str}")
                self.state = ContentState[state_str.upper()]
            elif url.startswith("gs://"):
                # gs://website-mod-imagen-outputs/draft/1.html  # noqa: E231
                self.bucket = url.replace("gs://", "").split("/")[0]
                self.blob = url.replace(f"gs://{self.bucket}/", "")  # noqa: E231
                self.content_id = self.blob.split("/")[-1][
                    0 : self.blob.split("/")[-1].index(".")
                ]
                state_str = self.blob.split("/")[0]
                self.state = ContentState[state_str.upper()]
        except Exception as e:
            print(f"[Error]Unable to parse storage url: {e}")
            raise e


class ContentUtil:
    def __init__(self, project_id: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.project_id = project_id

    def fetch_content_for_edit(self, content_id: str) -> Union[WebpageContent, None]:
        """
        Check if the blog is in-review and returns the reviewing content, otherwies,
        Check if the blog is in edit and returns the editing content, otherwise,
        Returns the production content
        """
        content = self.fetch_content_by_id(
            content_id=content_id, state=ContentState.REVIEW
        )
        if content is None:
            content = self.fetch_content_by_id(
                content_id=content_id, state=ContentState.DRAFT
            )

        if content is None:
            content = self.fetch_content_by_id(
                content_id=content_id, state=ContentState.PRODUCTION
            )
        return content

    def list_content(self, state: ContentState) -> list[str]:
        print(f"**state.value={state.value}")
        blogs = list_files(
            project_id=self.project_id,
            bucket_name=self.bucket_name,
            file_prefix=f"{state.value.lower()}",
        )
        return [
            blog["public_url"] for blog in blogs if "/blog/" not in blog["public_url"]
        ]

    def get_contentId_from_url(self, url: str) -> str:
        from urllib.parse import urlparse

        o = urlparse(url)
        print(f"*********{o.path}")
        if (
            o.path == ""
            or o.path == "/"
            or o.path.lower() == "/edit"
            or o.path.lower() == "/edit/"
        ):
            content_id = "home"
        elif url.lower().endswith("/edit") or url.lower().endswith("/edit/"):
            content_id = url.split("/")[-2].lower().replace(".json", "")
        elif url.lower().endswith("/review") or url.lower().endswith("/review/"):
            content_id = url.split("/")[-2].lower().replace(".json", "")
        else:
            content_id = url.split("/")[-1].lower().replace(".json", "")
        if content_id == "":
            print("***get_contentId_from_url is home")
            content_id = "home"
        print(f"***get_contentId_from_url is {content_id}")
        return content_id

    def list_content_ids(self, state: ContentState) -> list[str]:
        blogs = list_files(
            project_id=self.project_id,
            bucket_name=self.bucket_name,
            file_prefix=f"{state.value.lower()}",
        )
        return [
            self.get_contentId_from_url(blog["public_url"])
            for blog in blogs
            if "/blog/" not in blog["public_url"]
        ]

    def fetch_content_by_id(
        self, content_id: str, state: ContentState
    ) -> Union[WebpageContent, None]:
        blob = f"{state.value.lower()}/{content_id}.json"
        print(f"[Info]fetch_blog_content_by_id: {blob}")
        content_bytes = download_file(
            project_id=self.project_id, bucket_name=self.bucket_name, blob_name=blob
        )
        # print(f"[Info]content_bytes={content_bytes}")
        if content_bytes is not None:
            return WebpageContent(
                url=f"https://storage.googleapis.com/{self.bucket_name}/{blob}",  # noqa: E231
                content=content_bytes.decode(),
            )
        else:
            print(f"[Warning]No content found for {blob}")
            return None

    def move_content_to_new_state(
        self, content_id: str, oldState: ContentState, newState: ContentState
    ) -> str:
        try:
            if newState == ContentState.PRODUCTION:
                source_bytes = download_file(
                    project_id=self.project_id,
                    bucket_name=self.bucket_name,
                    blob_name=f"{oldState.value.lower()}/blog/{content_id}.json",
                )
                source_content = source_bytes.decode("utf-8")
                encoder = ContentEncoder()
                result = encoder.remove_comments(source_content)
                result_text = json.dumps(result)
                new_url = upload_file(
                    binary_content=result_text,
                    project_id=self.project_id,
                    bucket_name=self.bucket_name,
                    content_type="text/plain",
                    blob_name=f"{newState.value.lower()}/blog/{content_id}.json",
                )
                delete_file(
                    project_id=self.project_id,
                    bucket_name=self.bucket_name,
                    blob_name=f"{oldState.value.lower()}/blog/{content_id}.json",
                )
            else:
                new_url = move_file(
                    project_id=self.project_id,
                    source_bucket=self.bucket_name,
                    source_blob=f"{oldState.value.lower()}/{content_id}.json",
                    new_bucket=self.bucket_name,
                    new_blob=f"{newState.value.lower()}/{content_id}.json",
                )
            return new_url
        except Exception as e:
            print(f"[Error]move_content_to_new_state: {e}")
            raise e

    def copy_content(
        self, content_id: str, fromState: ContentState, toState: ContentState
    ) -> str:
        return copy_file(
            project_id=self.project_id,
            source_bucket=self.bucket_name,
            source_blob=f"{fromState.value.lower()}/{content_id}.json",
            new_bucket=self.bucket_name,
            new_blob=f"{toState.value.lower()}/{content_id}.json",
        )

    def fetch_content(self, url: str) -> WebpageContent:
        print(f"fetch_blog_content: {url}")
        b = WebpageContent(url=url)
        print(f"**b={b}")
        content_bytes = download_file(
            project_id=self.project_id, bucket_name=self.bucket_name, blob_name=b.blob
        )
        b.content = content_bytes.decode("utf-8")
        return b

    def delete_webcontent(self, file_name: str, state: ContentState) -> None:
        delete_file(
            project_id=self.project_id,
            bucket_name=self.bucket_name,
            blob_name=f"{state.value.lower()}/{file_name}",
        )

    def save_content(self, file_name: str, content: str, state: ContentState) -> str:
        encoder = ContentEncoder()
        content = encoder.ensure_json(content)

        return upload_file(
            binary_content=content,
            content_type="text/plain",
            project_id=self.project_id,
            bucket_name=self.bucket_name,
            blob_name=f"{state.value.lower()}/{file_name}",
        )
