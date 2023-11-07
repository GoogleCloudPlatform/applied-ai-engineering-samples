import logging; logging.basicConfig(level=logging.INFO)
import unittest

import marketing
import config

class MarketingTest(unittest.TestCase):

  def test_generate_marketing_copy(self):
    desc = 'New Men’s Nike Sportswear Storm-Fit Hooded Puffer Jacket   Retail~$200'
    attributes = ['Coat', 'Green']
    res = marketing.generate_marketing_copy(desc, attributes)
    self.assertIsInstance(res, str)
    logging.info(res)

if __name__ == '__main__':
  unittest.main()