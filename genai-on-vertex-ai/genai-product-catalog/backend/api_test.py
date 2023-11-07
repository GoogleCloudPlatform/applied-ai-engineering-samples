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
ENDPOINT = 'https://vijay-sandbox-335018.uc.r.appspot.com/v1/'

open_id_connect_token = id_token.fetch_id_token(Request(), 'client_id')
headers = {
    "Authorization": f"Bearer {open_id_connect_token}"
}
class APITest(unittest.TestCase):

  def test_category_get(self):
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

  def test_category_get_text_only(self):
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
    res = requests.get(
      ENDPOINT+'marketing/', 
      params={
        'description':'Kids jacket', 
        'attributes': ['rainbow', 'reversable']},
      headers=headers
      )
    self.assertEqual(res.status_code, 200)
    self.assertIsInstance(res.text,str)
    logging.info(res.text)

if __name__ == '__main__':
  unittest.main()