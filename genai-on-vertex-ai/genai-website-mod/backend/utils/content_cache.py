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

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.blog_utils import BlogUtil
from utils.content_utils import ContentState, ContentUtil  # noqa: F811
from utils.gcs import ContentState


class ContentCache(object):
    _instance = None
    static_files_dict: dict = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ContentCache, cls).__new__(cls)
            cls._instance.static_files_dict = {}
        return cls._instance

    def __init__(self, config: dict):
        self.config = config

    def get_blog_for_edit(self, blog_id: str) -> dict:
        blogUtil = BlogUtil(
            project_id=self.config["global"]["project_id"],
            bucket_name=self.config["blog"]["blog_bucket"],
        )
        content = blogUtil.fetch_content_for_edit(content_id=blog_id)
        if (
            content is not None
            and content.content is not None
            and content.content != ""
        ):
            o = json.loads(content.content)
            # o["state"] = content.state.value.lower()
            return o
        else:
            return {}

    def get_webcontent_by_state(self, content_id: str, state: ContentState) -> dict:
        util = ContentUtil(
            project_id=self.config["global"]["project_id"],
            bucket_name=self.config["blog"]["blog_bucket"],
        )
        webcontent = util.fetch_content_by_id(
            content_id=content_id, state=state
        )  # .fetch_content_for_edit(content_id=content_id)
        if (
            webcontent is not None
            and webcontent.content is not None
            and webcontent.content != ""
        ):
            return json.loads(webcontent.content)
        else:
            return {}

    def get_webcontent_for_edit(self, content_id: str) -> dict:
        util = ContentUtil(
            project_id=self.config["global"]["project_id"],
            bucket_name=self.config["blog"]["blog_bucket"],
        )
        webcontent = util.fetch_content_for_edit(content_id=content_id)
        if (
            webcontent is not None
            and webcontent.content is not None
            and webcontent.content != ""
        ):
            o = json.loads(webcontent.content)
            # o["state"] = webcontent.state.value.lower()
            return o
        else:
            return {}

    def get_blog_by_state(self, content_id: str, state: ContentState) -> dict:
        util = BlogUtil(
            project_id=self.config["global"]["project_id"],
            bucket_name=self.config["blog"]["blog_bucket"],
        )
        webcontent = util.fetch_content_by_id(
            content_id=content_id, state=state
        )  # .fetch_content_for_edit(content_id=content_id)
        if (
            webcontent is not None
            and webcontent.content is not None
            and webcontent.content != ""
        ):
            print(webcontent.content)
            return json.loads(webcontent.content)
        else:
            return {}

    def get_blog(self, blog_id: str) -> dict:
        blog = [
            b
            for b in self.static_files_dict["blog_data"]
            if str(b["blog_id"]) == str(blog_id)
        ]
        if len(blog) > 0:
            return blog[0]["blob"]
        else:
            return {}

    def get_content(self, key: str) -> dict:
        print(
            f"self.static_files_dict.keys()={self.static_files_dict.keys()} | key={key}"
        )
        if key in self.static_files_dict.keys():
            print(f"*** found content id: {key}")
            return self.static_files_dict[key]
        else:
            return {}

    def update_blog(self, blog_id: str, state=ContentState.PRODUCTION) -> None:
        blogUtil = BlogUtil(
            project_id=self.config["global"]["project_id"],
            bucket_name=self.config["blog"]["blog_bucket"],
        )
        blog = blogUtil.fetch_content_by_id(content_id=blog_id, state=state)
        print(f"*** blog is None={blog is None}")
        print(f"{'blog_data' not in self.static_files_dict}")
        if blog is not None and "blog_data" not in self.static_files_dict:
            self.static_files_dict["blog_data"] = []
            self.static_files_dict["blog_data"].append(
                {"blog_id": blog.blog_id, "blob": json.loads(blog.content)}
            )
        else:
            for cached_content in self.static_files_dict["blog_data"]:
                if str(cached_content["blog_id"]) == str(blog_id) and blog is not None:
                    self.static_files_dict["blog_data"].remove(cached_content)
                    self.static_files_dict["blog_data"].append(
                        {"blog_id": blog.blog_id, "blob": json.loads(blog.content)}
                    )
                    break

    def update_content(self, content_id: str, state=ContentState.PRODUCTION) -> None:
        util = ContentUtil(
            project_id=self.config["global"]["project_id"],
            bucket_name=self.config["blog"]["blog_bucket"],
        )
        webcontent = util.fetch_content_by_id(content_id=content_id, state=state)
        print(f"[INFO][DEBUG]={content_id} | state={state}")
        for cid in self.static_files_dict.keys():
            if str(cid) == str(content_id) and webcontent is not None:
                print(f"[INFO][DEBUG]webcontent is not None:cid={cid}")
                self.static_files_dict[cid] = json.loads(webcontent.content)
                break

    def refresh(
        self, refresh_blogs: bool = False, refresh_content: bool = False
    ) -> dict:
        if refresh_blogs:
            if "blog_data" not in self.static_files_dict:
                self.static_files_dict["blog_data"] = []

            blogUtil = BlogUtil(
                project_id=self.config["global"]["project_id"],
                bucket_name=self.config["blog"]["blog_bucket"],
            )
            static_files = blogUtil.list_contents(state=ContentState.PRODUCTION)
            for blog_url in static_files:
                print(f"***fecthing blog: {blog_url}")
                blog_content = blogUtil.fetch_content(blog_url=blog_url)
                self.static_files_dict["blog_data"].append(
                    {
                        "blog_id": blog_content.blog_id,
                        "blob": json.loads(blog_content.content),
                    }
                )

        if refresh_content:
            contentUtil = ContentUtil(
                project_id=self.config["global"]["project_id"],
                bucket_name=self.config["blog"]["blog_bucket"],
            )
            static_files = contentUtil.list_content(state=ContentState.PRODUCTION)
            for content_url in static_files:
                web_content = contentUtil.fetch_content(url=content_url)
                print(f"***refresh_content={web_content.content_id}")
                self.static_files_dict[web_content.content_id] = json.loads(
                    web_content.content
                )
                # self.static_files_dict[content.content_id] = content.content
        print(self.static_files_dict.keys())
        return self.static_files_dict
