"""Vertex Embedding API Integration Test.

Ensures we can call the Vertex Embedding API and embeddings are returned in 
the expected format. As this is a cloud API this test will need to run from
a GCP authenticated environment

https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings
"""
import unittest
import embeddings

PROJECT_ID = 'solutions-2023-mar-107'

class EmbeddingsTest(unittest.TestCase):

  def test_embeddings_api(self):
    res = embeddings.embed(
        PROJECT_ID,
        "IZOD Women's Light Gray Thigh Length Pull On Golf Shorts",
        'gs://genai-product-catalog/toy_images/shorts.jpg',
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertEqual(len(res.image_embedding), 1408)

if __name__ == '__main__':
  unittest.main()