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

from pydantic import BaseModel


class CaptionImageRequest(BaseModel):
    image_url: str = ""


class CaptionImageResponse(BaseModel):
    captions: list[str] = []


class GenerateImagesRequest(BaseModel):
    prompt: str = ""


class GenerateImagesResponse(BaseModel):
    image_urls: list[str] = []


class RefineImagesRequest(BaseModel):
    image_url: str
    target_region: str


class RefineImagesResponse(BaseModel):
    image_urls: list[str] = []
