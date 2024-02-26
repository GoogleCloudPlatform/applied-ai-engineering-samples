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

# flake8: noqa

import glob
import json

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

static_files_dir = "views/json"
static_files_dict: dict = {}

static_files = glob.glob(static_files_dir + "/*.json")


class SaveDataRequest(BaseModel):
    saved_data: dict
    file_path: str


class FetchUrlDataRequest(BaseModel):
    url: str


@router.get(path="/fetch-url-data")
async def fetch_url_data(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            print(response)

            if response.status_code == 200:
                print(response)

                data = {
                    "success": 1,
                    "meta": {
                        "title": "Currency Arbitrage: The Alluring Illusion of Risk-Free Profit",
                        "description": "Currency arbitrage might seem like a risk-free way to make money, but why should you be wary of it?",
                        "image": {
                            "url": "https://storage.googleapis.com/website-mod-blog-images/images/1e1ddca4-f20f-42d4-a514-74d336aac3ec.jpg"
                        },
                    },
                }

                return data
            else:
                raise HTTPException(
                    status_code=response.status_code, detail="Failed to fetch data"
                )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@router.post(path="/echo")
def echo(text: str) -> str:
    return text


def parse_file_path(file_path):
    list_link = file_path.split("/")
    page = list_link[-1].split(".")[0]
    return page


def blog_saved_data(page_id):
    blogs_content = []
    blog_files = glob.glob(static_files_dir + "/blog/*.json")

    for blog_file in blog_files:
        with open(blog_file, "r") as file:
            page_id = parse_file_path(blog_file)

            blog_content = json.load(file)
            blog_dict = {"blog_id": int(page_id), "blob": blog_content}
            blogs_content.append(blog_dict)
            file.close()

    with open(f"{static_files_dir}/blog_data.json", "w") as file:
        file.write(json.dumps(blogs_content, indent=4))
        file.close()
    print("blogs combined correctly")


@router.post(path="/save-js")
def save_js(request: SaveDataRequest):
    saved_data = request.saved_data
    page_id = parse_file_path(request.file_path)
    combine_blogs = False

    if page_id in ["1", "2", "3", "4", "5", "6"]:
        save_path = f"{static_files_dir}/blog/{page_id}.json"
        combine_blogs = True
    else:
        save_path = f"{static_files_dir}/{page_id}.json"

    try:
        with open(save_path, "w") as file:
            js_content = json.dumps(saved_data, indent=4)
            file.write(js_content)
            file.close()

    except Exception as e:
        return JSONResponse(
            content={"message": f"Error saving data: {str(e)}"}, status_code=500
        )

    if combine_blogs:
        blog_saved_data(page_id)

    return {"message": "Data saved successfully"}
