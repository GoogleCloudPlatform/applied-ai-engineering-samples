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

import base64
import json
import logging
from typing import Any, Dict

import functions_framework
from google.cloud import firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.cloud_event
def pubsub_to_firestore(cloud_event: Dict[str, Any]) -> str:
  """Cloud Function triggered by Pub/Sub to write or update messages in Firestore.

  This function reads the Pub/Sub message from a Dataflow success pipeline
  and writes or updates it in Firestore.

  Args:
      cloud_event (Dict[str, Any]): The cloud event containing the Pub/Sub
        message.

  Returns:
      str: 'OK' if the operation is successful.
  """
  # Get the Pub/Sub message from Dataflow success pipeline
  pubsub_message = base64.b64decode(
      cloud_event.data["message"]["data"]
  ).decode()
  message_data = json.loads(pubsub_message)

  logger.info(f"Received Pub/Sub message: {message_data}")

  # Initialize Firestore client
  db = firestore.Client()

  # Prepare the document to be written
  doc_data = {
      "vector_store": message_data.get("vector_store", {}),
      "last_updated": firestore.SERVER_TIMESTAMP,
  }

  # Use index_name as the document key
  index_name = message_data.get("index_name", "unknown")
  doc_ref = db.collection("rp_indices").document(index_name)

  logger.info(f"Writing data to Firestore for index: {index_name}")

  # Merge the new data with existing data (if any)
  doc_ref.set(doc_data, merge=True)

  logger.info(
      f"Successfully wrote/updated message in Firestore for index: {index_name}"
  )

  return "OK"
