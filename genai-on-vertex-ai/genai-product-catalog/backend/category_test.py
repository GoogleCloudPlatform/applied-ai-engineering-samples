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

"""Category Unit and Integration Tests.

These tests assume:
-The appropriate variables have been set in config.py
-The test is run from an environment that has permission to call cloud APIs
"""
import logging; logging.basicConfig(level=logging.INFO)
import unittest

import category
import config

class CategoryTest(unittest.TestCase):

  def test_join_categories(self):
    res = category.join_categories([config.TEST_PRODUCT_ID])
    logging.info(res)
    self.assertIsNotNone(res.get(config.TEST_PRODUCT_ID))
    self.assertIsInstance(res[config.TEST_PRODUCT_ID],list)
    self.assertIsInstance(res[config.TEST_PRODUCT_ID][0],str)

  def test_retrieve(self):
    res = category.retrieve(
        'This is a test description',
        config.TEST_GCS_IMAGE
    )
    logging.info(res)
    self.assertIsInstance(res, list)
    self.assertEqual(len(res), config.NUM_NEIGHBORS*2)
    self.assertEqual(set(res[0].keys()), {'id','category','distance'})

  def test_rank(self):
    candidates = [('cat1_a','cat2_a'), ('cat1_b','cat2_b')]
    res = category.rank(
        'This is a test description',
        candidates
    )
    logging.info(res)
    self.assertEqual(sorted(candidates),sorted(res))

  def test_retrieve_and_rank(self):
    res = category.retrieve_and_rank(
        'This is a test description',
        config.TEST_GCS_IMAGE
    )
    logging.info(res)
    self.assertIsInstance(res, list)
    self.assertGreater(len(res),0)

  def test_retrieve_and_rank_with_filter(self):
    res = category.retrieve_and_rank(
        'This is a test description',
        config.TEST_GCS_IMAGE,
        filters=[config.TEST_CATEGORY_L0]
    )
    logging.info(res)
    self.assertIsInstance(res, list)
    self.assertGreater(len(res),0)

  def test_retrieve_and_rank_with_bad_filter(self):
    res = category.retrieve_and_rank(
        'This is a test description',
        config.TEST_GCS_IMAGE,
        filters=['XYZunknowncategory']
    )
    logging.info(res)
    self.assertIsInstance(res, list)
    self.assertGreater(len(res),0)

if __name__ == '__main__':
  unittest.main()