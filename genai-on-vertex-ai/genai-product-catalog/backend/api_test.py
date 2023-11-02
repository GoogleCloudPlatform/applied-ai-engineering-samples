"""Test Rest API.

Make sure to update the ENDPOINT variable as appropriate before running.
"""
import logging
import requests
import unittest
import api
import config

ENDPOINT = 'http://localhost:8080/v1/'

class APITest(unittest.TestCase):

  def test_category_get(self):
    image_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    res = requests.post(ENDPOINT+'categories', json={'description':'test description', 'image':image_base64})
    logging.debug(res.json())
    self.assertEqual(res.status_code, 200)

  def test_category_get_text_only(self):
    res = requests.post(ENDPOINT+'categories', json={'description':'test description'})
    logging.debug(res.json())
    self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
  unittest.main()