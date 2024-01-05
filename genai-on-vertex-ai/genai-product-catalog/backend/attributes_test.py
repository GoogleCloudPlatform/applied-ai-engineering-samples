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

  def test_join_attributes_desc(self):
    res = attributes.join_attributes_desc([config.TEST_PRODUCT_ID])
    self.assertIsNotNone(res)
    self.assertIsInstance(res,dict)
    for k,v in res.items():
      self.assertIsInstance(k,str)
      self.assertIsInstance(v,dict)
      self.assertEqual(set(v.keys()), {'attributes','description'})
    logging.info(res[config.TEST_PRODUCT_ID]['attributes'])
    logging.info(res[config.TEST_PRODUCT_ID]['description'])

  def test_generate_prompt(self):
    desc = 'This is an orange'
    candidates = [
      {'description': 'Apple', 'attributes': {'Color':'green', 'Taste':'sweet'}},
      {'description': 'Banana', 'attributes': {'Color': 'yellow'}},
    ]
    res = attributes.generate_prompt(desc, candidates)
    logging.info(res)
    self.assertIsInstance(res, str)

  def test_retrieve_no_category(self):
    res = attributes.retrieve(
        'This is a test description',
        None,
        config.TEST_GCS_IMAGE
    )
    logging.info(res)
    self.assertIsInstance(res, list)
    self.assertEqual(len(res), config.NUM_NEIGHBORS*2)
    self.assertEqual(set(res[0].keys()), {'id','attributes','description','distance'})

  def test_generate_attributes_no_category(self):
    candidates = [
      {'description': 'Apple', 'attributes': {'Color':'green', 'Taste':'sweet'}},
      {'description': 'Banana', 'attributes': {'Color': 'yellow'}},
    ]
    res = attributes.generate_attributes(
        'Orange',
        candidates
    )
    logging.info(res)
    self.assertIsInstance(res, dict)
    self.assertGreater(len(res),0)

  def test_parse_answer(self):
    res = attributes.parse_answer(' color: deep red |size:large')
    self.assertDictEqual(res, {'color':'deep red','size':'large'})

  def test_retrieve_and_generate_attributes(self):
    res = attributes.retrieve_and_generate_attributes(
        'Fleece Jacket',
        None,
        config.TEST_GCS_IMAGE
    )
    logging.info(res)
    self.assertIsInstance(res, dict)
    self.assertGreater(len(res),0)

  def test_retrieve_and_generate_attributes_with_filter(self):
    res = attributes.retrieve_and_generate_attributes(
        'Fleece Jacket',
        None,
        config.TEST_GCS_IMAGE,
        filters=[config.TEST_CATEGORY_L0],
    )
    logging.info(res)
    self.assertIsInstance(res, dict)
    self.assertGreater(len(res),0)

  def test_retrieve_and_generate_attributes_with_bad_filter(self):
    res = attributes.retrieve_and_generate_attributes(
        'Fleece Jacket',
        None,
        config.TEST_GCS_IMAGE,
        filters=['XYZunknowncategory'],
    )
    logging.info(res)
    self.assertIsInstance(res, dict)
    self.assertGreater(len(res),0)

if __name__ == '__main__':
  unittest.main()