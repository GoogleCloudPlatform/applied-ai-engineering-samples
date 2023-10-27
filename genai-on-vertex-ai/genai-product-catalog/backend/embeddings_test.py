"""Vertex Embedding API Integration Test.

Ensures we can call the Vertex Embedding API and embeddings are returned in 
the expected format. This integration test assumes:
-The appropriate constants have been set in config.py
-The test is run from an environment that has permission to call the API

https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings
"""
import unittest
import config
import embeddings

class EmbeddingsTest(unittest.TestCase):

  def test_embeddings_api(self):
    res = embeddings.embed(
        config.PROJECT,
        'This is a test description',
        config.GCS_TEST_IMAGE,
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertEqual(len(res.image_embedding), 1408)

if __name__ == '__main__':
  unittest.main()