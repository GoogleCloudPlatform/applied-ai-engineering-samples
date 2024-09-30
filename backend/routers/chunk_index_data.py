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
from fastapi import APIRouter, HTTPException
from models.index_data import PubSubMessage
from utils.pubsub_index_utils import publish_message

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(path="/trigger-indexing-job")
def create_indexing_job(data: PubSubMessage):
  """Trigger an indexing job by publishing a message to Pub/Sub.

  Args:
      data (PubSubMessage): The message to be published.

  Returns:
      dict: A dictionary containing the status and result message.

  Raises:
      HTTPException: If an error occurs while publishing the message.
  """
  try:
    logger.info("Triggering indexing job")
    result = publish_message(data.model_dump_json())
    logger.info("Indexing job triggered successfully")
    return {"status": "success", "message": result}
  except Exception as e:
    logger.error(f"Error triggering indexing job: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/get-index-request")
def print_request(data: PubSubMessage):
  """Print the index request data.

  Args:
      data (PubSubMessage): The index request data.

  Returns:
      dict: The index request data as a dictionary.
  """
  logger.info("Received index request")
  return data.model_dump()
