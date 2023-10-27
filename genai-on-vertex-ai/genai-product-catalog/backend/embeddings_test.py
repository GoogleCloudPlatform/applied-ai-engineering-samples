import unittest
import embeddings

PROJECT_ID = 'solutions-2023-mar-107'

class EmbeddingsTest(unittest.TestCase):

  def test_embeddings_api(self):
    """
    Note this is more of an integration test than a unit test. It ensures
    The Vertex Embedding API client code works and the API returns data
    in the expected format
    """
    res = embeddings.embed(
        PROJECT_ID,
        "IZOD Women's Light Gray Thigh Length Pull On Golf Shorts",
        'gs://genai-product-catalog/toy_images/shorts.jpg',
    )
    self.assertEqual(len(res.text_embedding), 1408)
    self.assertEqual(len(res.image_embedding), 1408)

if __name__ == '__main__':
  unittest.main()