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

import json
import logging
import apache_beam as beam
from apache_beam.io import PubsubMessage


class WriteSuccessMessageFn(beam.DoFn):

  def process(self, element):
    value = element
    logging.info(f'Received Successful element: {json.dumps(value)}')

    vector_store_config = value.get('vector_store', {}).get('config', {})

    # Prepare all data to be included in the message body
    success_message = {
        'index_name': vector_store_config.get('index_name', 'unknown'),
        'vector_store': {
            'project_id': vector_store_config.get('project_id', 'unknown'),
            'region': vector_store_config.get('region', 'unknown'),
            'index_id': vector_store_config.get('index_id', 'unknown'),
            'endpoint_id': vector_store_config.get('endpoint_id', 'unknown'),
        },
        'original_message': value,
    }

    data = bytes(json.dumps(success_message), 'utf-8')

    # Create PubsubMessage with empty attributes
    message = PubsubMessage(data=data, attributes={})

    logging.info(f'Writing message to Pub/Sub: {success_message}')
    return [message]  # Use return instead of yield
