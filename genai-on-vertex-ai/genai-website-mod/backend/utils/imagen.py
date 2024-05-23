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

from fastapi import APIRouter
from vertexai.preview.vision_models import (
    Image,
    ImageCaptioningModel,
    ImageGenerationModel,
    ImageGenerationResponse,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


router = APIRouter()


def caption_image(image_bytes: bytes, model_name="imagetext@001") -> list[str]:
    model = ImageCaptioningModel.from_pretrained(model_name)
    source_image = Image(image_bytes=image_bytes)

    captions = model.get_captions(
        image=source_image,
        number_of_results=1,
        language="en",
    )

    return captions


def generate_image(
    prompt: str, negative_prompt: str = "", model_name="imagegeneration@006"
) -> ImageGenerationResponse:
    model = ImageGenerationModel.from_pretrained(model_name)
    images = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        negative_prompt=negative_prompt,
        add_watermark=True,
    )
    return images


def edit_image(image_bytes: bytes, prompt: str, model_name="imagegeneration@002"):
    model = ImageGenerationModel.from_pretrained(model_name)
    base_img = Image(image_bytes=image_bytes)

    images = model.edit_image(
        base_image=base_img,
        prompt=prompt,
        seed=1,
        guidance_scale=20,
        number_of_images=1,
    )
    return images
