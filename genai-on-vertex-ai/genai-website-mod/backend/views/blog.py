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

import glob
import json
import tomllib

from utils.blog_utils import BlogUtil
from utils.gcs import ContentState

with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

blog_dir = "json/blog"

blogs_content = []

blog_files = glob.glob(blog_dir + "/*.json")

file_dict: dict = {}

blogUtil = BlogUtil(
    project_id=config["global"]["project_id"], bucket_name=config["blog"]["blog_bucket"]
)
blog_urls = blogUtil.list_contents(state=ContentState.PRODUCTION)
for blog_url in blog_urls:
    content = blogUtil.fetch_content(blog_url=blog_url)
    blogs_content.append(content)

with open("blog_data.json", "w") as f:
    f.write(json.dumps(blogs_content, indent=4))
