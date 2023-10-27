"""Vertex Vector Search Integration Test.

Ensures we can access the vector store and nearest neighbors are returned 
the expected format. This integration test assumes:
-A Vector Store is already running and the appropriate variables have been set 
in config.py
-The test is run from an environment that has permission to call the API

https://cloud.google.com/vertex-ai/docs/vector-search/overview
"""
import unittest
import nearest_neighbors

class NearestNeighborsTest(unittest.TestCase):

  def test_nn(self):
    emb1 = [0] * 1408
    emb2 = [0] * 1408
    embeds = [emb1, emb2]
    num_neigbhors = 3
    res = nearest_neighbors.get_nn(embeds, num_neigbhors)
    self.assertEqual(len(res), len(embeds) * num_neigbhors)
    self.assertEqual(res[0]._fields, ('id','distance'))

if __name__ == '__main__':
  unittest.main()