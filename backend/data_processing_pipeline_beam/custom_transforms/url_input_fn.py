# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import apache_beam as beam


class URLInputFn(beam.DoFn):
  """DoFn for processing URL input elements."""

  def process(self, element):
    """Process a URL input element.

    Args:
        element (dict): The input element containing URL configuration.

    Yields:
        dict: A dictionary containing the processed URL and base element.
    """
    try:
      logging.info(f"Received URLInputFn: {element}")
      input_config = element["input"]["config"]

      yield {
          "type": "url",
          "url": input_config["url"],
          "base_element": element,
      }

    except Exception as e:
      logging.error(f"Error processing input: {str(e)}")
