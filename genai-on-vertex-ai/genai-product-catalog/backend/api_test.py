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

"""Test Rest API.

Make sure to update the ENDPOINT variable as appropriate before running.
"""
import logging; logging.basicConfig(level=logging.INFO)
import requests
import unittest
import api
import config

from google.auth.transport.requests import Request
from google.oauth2 import id_token

ENDPOINT = 'http://localhost:8080/v1/'
#ENDPOINT = 'https://vijay-sandbox-335018.uc.r.appspot.com/v1/'

open_id_connect_token = id_token.fetch_id_token(Request(), 'client_id')
headers = {
    "Authorization": f"Bearer {open_id_connect_token}"
}
class APITest(unittest.TestCase):

  def test_category(self):
    image_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    res = requests.post(
      ENDPOINT+'categories/', 
      json={'description':'test description', 'image':image_base64},
      headers=headers
      )
    self.assertEqual(res.status_code, 200)
    self.assertIsInstance(res.json(),list)
    self.assertIsInstance(res.json()[0],list)
    self.assertIsInstance(res.json()[0][0],str)
    logging.info(res.json())

  def test_category_text_only(self):
    res = requests.post(
      ENDPOINT+'categories/', 
      json={'description':'test description'},
      headers=headers
      )
    self.assertEqual(res.status_code, 200)
    self.assertIsInstance(res.json(),list)
    self.assertIsInstance(res.json()[0],list)
    self.assertIsInstance(res.json()[0][0],str)
    logging.info(res.json())

  def test_generate_marketing_copy(self):
    res = requests.post(
      ENDPOINT+'marketing/', 
      params={'description':'Mens Hooded Puffer Jacket'},
      json={'attributes': '{"color":"green", "material": "down"}'},
      headers=headers
      )
    self.assertEqual(res.status_code, 200)
    self.assertIsInstance(res.text,str)
    logging.info(res.text)

  def test_attributes(self):
    image_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    res = requests.post(
      ENDPOINT+'attributes/', 
      json={'description':'test description', 'image':image_base64},
      headers=headers
      )
    self.assertEqual(res.status_code, 200)
    self.assertIsInstance(res.json(),dict)
    self.assertGreater(len(res.json()),0)
    logging.info(res.json())

if __name__ == '__main__':
  unittest.main()