#!/usr/bin/env python

# Copyright 2019 Google LLC
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

import argparse
import json

from google.cloud import pubsub_v1

from google.pubsub_v1 import types as gapic_types
#from google.pubsub_v1.services.publisher import client as publisher_client
from google.pubsub_v1.services.publisher.client import PublisherClient
from google.pubsub_v1.types import Encoding
from google.protobuf.json_format import MessageToJson


def pub(project_id: str, topic_id: str) -> None:
    """Publishes a message to a Pub/Sub topic."""
    ## Initialize a Publisher client.
    #client = pubsub_v1.PublisherClient()
    ## Create a fully qualified identifier of form `projects/{project_id}/topics/{topic_id}`
    client = PublisherClient()
    topic_path = client.topic_path(project_id, topic_id)
    topic = client.get_topic(topic=topic_path)
    encoding = topic.schema_settings.encoding
    # Assume that encoding is JSON
    if encoding != Encoding.JSON:
        raise ValueError("Unsupported topic encoding")

    data = {
        "request_type" :  "lll",
        "request_name": "aaa",
        "response_length": 2,
        "start_time": "2018-11-11"
    }
    #data_json = json.dumps(data)
    data_json = str(json.dumps(data)).encode("utf-8")
    print(data_json)

    message = {
        'data': data_json 
    }

   # message = {
   #        'request_type': "saxml",
   #        'request_name': 'lm.generat',
   #        'response_length': 100,
   #        'start_time':  '2008-12-24',
   # }

    response = client.publish(topic=topic_path, messages=[message])

    #print(f"Published {data.decode()} to {topic_path}: {message_id}")


if __name__ == "__main__":
    #parser = argparse.ArgumentParser(
    #    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    #)
    #parser.add_argument("project_id", default="jk-mlops-dev", help="Google Cloud project ID")
    #parser.add_argument("topic_id", default="locust-pubsub-sink", help="Pub/Sub topic ID")

    #args = parser.parse_args()

    project_id='jk-mlops-dev'
    topic_id='locust_pubsub_sink'

    pub(project_id, topic_id)
