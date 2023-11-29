# Copyright 2023 Google LLC
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

"""Invoke Vertex Embedding API."""

import base64
from functools import cache
import time
import logging
from typing import NamedTuple, Optional, Sequence

from google.cloud import aiplatform
from google.protobuf import struct_pb2

import config

class EmbeddingResponse(NamedTuple):
  text_embedding: Sequence[float]
  image_embedding: Sequence[float]


class EmbeddingPredictionClient:
  """Wrapper around Prediction Service Client."""
  def __init__(self, project : str,
    location : str = "us-central1",
    api_regional_endpoint: str = "us-central1-aiplatform.googleapis.com"):
    client_options = {"api_endpoint": api_regional_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    self.client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    self.location = location
    self.project = project

  def get_embedding(self, text: Optional[str] = None, 
                    image: Optional[str] = None, base64: bool = False):
    """Invoke Vertex multimodal embedding API.
    
    You can pass text and/or image. If neither is passed will raise exception

    Args:
      text: text to embed
      image: can be local file path, GCS URI or base64 encoded image
      base64: True indicates image is base64. False (default) will be 
        interpreted as image path (either local or GCS)
    Returns:
    named tuple with the following attributes:
      text_embedding: 1408 dimension vector of type Sequence[float]
      image_embedding: 1408 dimension vector of type Sequence[float] OR None if
        no image provide
    """
    if not text and not image:
      raise ValueError('At least one of text or image_bytes must be specified.')

    instance = struct_pb2.Struct()
    if text:
      if len(text) >= 1024:
        logging.warning('Text must be less than 1024 characters. Truncating text.')
        text = text[:1023]
      instance.fields['text'].string_value = text

    if image:
      image_struct = instance.fields['image'].struct_value
      if base64:
        image_struct.fields['bytesBase64Encoded'].string_value = image
      elif image.lower().startswith('gs://'):
        image_struct.fields['gcsUri'].string_value = image
      else:
        with open(image, "rb") as f:
          image_bytes = f.read()
        encoded_content = base64.b64encode(image_bytes).decode("utf-8")
        image_struct.fields['bytesBase64Encoded'].string_value = encoded_content

    instances = [instance]
    endpoint = (f"projects/{self.project}/locations/{self.location}"
      "/publishers/google/models/multimodalembedding@001")
    response = self.client.predict(endpoint=endpoint, instances=instances)

    text_embedding = None
    if text:
      text_emb_value = response.predictions[0]['textEmbedding']
      text_embedding = [v for v in text_emb_value]

    image_embedding = None
    if image:
      image_emb_value = response.predictions[0]['imageEmbedding']
      image_embedding = [v for v in image_emb_value]

    return EmbeddingResponse(
      text_embedding=text_embedding,
      image_embedding=image_embedding)



@cache
def get_client(project):
  return EmbeddingPredictionClient(project)


def embed(
  text: str,
  image: Optional[str] = None,
  base64: bool = False, 
  project: str = config.PROJECT) -> EmbeddingResponse:
  """Invoke vertex multimodal embedding API.

  Args:
    text: text to embed
    image: can be local file path, GCS URI or base64 encoded image
    base64: True indicates image is base64. False (default) will be 
        interpreted as image path (either local or GCS)
    project: GCP Project ID

  Returns:
    named tuple with the following attributes:
      text_embedding: 1408 dimension vector of type Sequence[float]
      image_embedding: 1408 dimension vector of type Sequence[float] OR None if
        no image provide
  """
  client = get_client(project)
  start = time.time()
  response = client.get_embedding(text=text, image=image, base64=base64)
  end = time.time()
  return response
