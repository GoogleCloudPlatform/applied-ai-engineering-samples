"""Attribute Unit and Integration Tests.

These tests assume:
-The appropriate variables have been set in config.py
-The test is run from an environment that has permission to call cloud APIs
"""
import logging; logging.basicConfig(level=logging.INFO)
import unittest

import attributes
import config

class AttributesTest(unittest.TestCase):

  def test_join_attributes(self):
    res = attributes.join_attributes([config.TEST_PRODUCT_ID])
    logging.info(res)
    self.assertIsNotNone(res)
    self.assertIsInstance(res,dict)
    for k,v in res.items():
      self.assertIsInstance(k,str)
      self.assertIsInstance(v,dict)


  def test_retrieve_no_category(self):
    res = attributes.retrieve(
        'This is a test description',
        None,
        config.TEST_GCS_IMAGE
    )
    logging.info(res)
    self.assertIsInstance(res, list)
    self.assertEqual(len(res), config.NUM_NEIGHBORS*2)
    self.assertEqual(set(res[0].keys()), {'id','attributes','distance'})

  def test_generate_no_category(self):
    res = attributes.generate_attributes(
        'This is a test description',
        None,
        config.TEST_GCS_IMAGE
    )
    logging.info(res)
    self.assertIsInstance(res, dict)
    self.assertGreater(len(res),0)

if __name__ == '__main__':
  unittest.main()