"""Client code for Vertex Multimodal Embeddings API."""

import base64
from functools import cache
import time
import typing

from google.genaisa.proton import bootstrap
from google.protobuf import struct_pb2


class EmbeddingResponse(typing.NamedTuple):
  text_embedding: typing.Sequence[float]
  image_embedding: typing.Sequence[float]


class EmbeddingPredictionClient:
  """Wrapper around Prediction Service Client."""

  def __init__(
      self,
      project: str,
      location: str = 'us-central1',
      api_regional_endpoint: str = 'us-central1-aiplatform.googleapis.com',
  ):
    client_options = {'api_endpoint': api_regional_endpoint}
    # Initialize client that will be used to create and send requests.
    self.client = bootstrap.load_prediction_client(
        project, client_options=client_options
    )
    self.location = location
    self.project = project

  def get_embedding(self, text: str = None, image_path: str = None):
    """image_path can be a local path or a GCS URI."""
    if not text and not image_path:
      raise ValueError('At least one of text or image_bytes must be specified.')

    instance = struct_pb2.Struct()
    if text:
      instance.fields['text'].string_value = text

    if image_path:
      image_struct = instance.fields['image'].struct_value
      if image_path.lower().startswith('gs://'):
        image_struct.fields['gcsUri'].string_value = image_path
      else:
        with open(image_path, 'rb') as f:
          image_bytes = f.read()
        encoded_content = base64.b64encode(image_bytes).decode('utf-8')
        image_struct.fields['bytesBase64Encoded'].string_value = encoded_content

    instances = [instance]
    endpoint = (
        f'projects/{self.project}/locations/{self.location}'
        '/publishers/google/models/multimodalembedding@001'
    )
    response = self.client.predict(endpoint=endpoint, instances=instances)

    text_embedding = None
    if text:
      text_emb_value = response.predictions[0]['textEmbedding']
      text_embedding = [v for v in text_emb_value]

    image_embedding = None
    if image_path:
      image_emb_value = response.predictions[0]['imageEmbedding']
      image_embedding = [v for v in image_emb_value]

    return EmbeddingResponse(
        text_embedding=text_embedding, image_embedding=image_embedding
    )


@cache
def get_client(project):
  return EmbeddingPredictionClient(project)


def embed(project, text, image_path=None):
  client = get_client(project)
  start = time.time()
  response = client.get_embedding(text=text, image_path=image_path)
  end = time.time()
  print('Embedding Time: ', end - start)
  return response