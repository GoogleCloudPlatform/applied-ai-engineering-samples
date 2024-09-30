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

from concurrent import futures
import logging
from typing import Callable
from google.cloud import pubsub_v1
from .firestore_utils import get_config_section

logger = logging.getLogger(__name__)

pubsub_config = get_config_section("pubsub")

PROJECT_ID = pubsub_config.get("project_id")
TOPIC_ID = pubsub_config.get("topic_id")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def get_callback(
    publish_future: pubsub_v1.publisher.futures.Future, data: str
) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
  """Create a callback function for the publish operation.

  Args:
      publish_future (pubsub_v1.publisher.futures.Future): The future object for
        the publish operation.
      data (str): The data being published.

  Returns:
      Callable[[pubsub_v1.publisher.futures.Future], None]: The callback
      function.
  """

  def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
    try:
      # Wait 60 seconds for the publish call to succeed.
      publish_future.result(timeout=60)
      logger.info(f"Message published successfully: {data[:100]}...")
    except futures.TimeoutError:
      logger.error(f"Publishing {data[:100]}... timed out.")

  return callback


def publish_message(data: str) -> str:
  """Publish a message to the Pub/Sub topic.

  Args:
      data (str): The message data to publish.

  Returns:
      str: A success message if the publish operation completes.

  Raises:
      Exception: If an error occurs while publishing the message.
  """
  message_bytes = data.encode("utf-8")

  try:
    publish_future = publisher.publish(topic_path, message_bytes)
    publish_future.add_done_callback(get_callback(publish_future, data))

    futures.wait([publish_future], return_when=futures.ALL_COMPLETED)

    logger.info(f"Message published successfully to {topic_path}")
    return f"Message published successfully to {topic_path}"
  except Exception as e:
    logger.error(f"An error occurred while publishing the message: {str(e)}")
    raise Exception(f"An error occurred while publishing the message: {str(e)}")
