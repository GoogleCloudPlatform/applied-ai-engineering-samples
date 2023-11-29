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

"""Vertex Embedding API Integration Test.

Ensures we can call the Vertex Embedding API and embeddings are returned in 
the expected format. This integration test assumes:
-The appropriate variables have been set in config.py
-The test is run from an environment that has permission to call the API

https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings
"""
import unittest
import config
import embeddings

class EmbeddingsTest(unittest.TestCase):

  def test_embeddings_api(self):
    res = embeddings.embed(
        'This is a test description',
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertIsNone(res.image_embedding)

  def test_embeddings_api_long_text(self):
    res = embeddings.embed(
        'This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters. This is a description longer than 1024 characters.',
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertIsNone(res.image_embedding)

  def test_embeddings_api_with_image(self):
    res = embeddings.embed(
        'This is a test description',
        config.TEST_GCS_IMAGE,
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertEqual(len(res.image_embedding), 1408)

  def test_embeddings_api_with_image_base64(self):
    image_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    res = embeddings.embed(
        'This is a test description',
        image_base64,
        base64=True
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertEqual(len(res.image_embedding), 1408)

if __name__ == '__main__':
  unittest.main()