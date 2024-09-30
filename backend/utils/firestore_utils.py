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
from typing import Any, Callable, Dict
from firebase_admin import credentials
from google.cloud.firestore import Client

logger = logging.getLogger(__name__)

# Initialize Firebase app
cred = credentials.ApplicationDefault()
db = Client()


def get_config() -> Dict[str, Any]:
  """Retrieve the entire configuration from Firestore.

  Returns:
      Dict[str, Any]: The configuration dictionary.

  Raises:
      Exception: If no config document is found in the database.
  """
  doc_ref = db.collection("config").document("app_config")
  doc = doc_ref.get()
  if doc.exists:
    logger.info("Retrieved configuration from Firestore")
    return doc.to_dict()
  else:
    logger.error("No config document found in rp-config-db database")
    raise Exception("No config document found in rp-config-db database!")


def get_config_section(section: str) -> Dict[str, Any]:
  """Retrieve a specific section of the configuration.

  Args:
      section (str): The name of the configuration section to retrieve.

  Returns:
      Dict[str, Any]: The configuration section as a dictionary.
  """
  config = get_config()
  logger.info(f"Retrieved configuration section: {section}")
  return config.get(section, {})


def watch_config(callback: Callable[[Dict[str, Any]], None]):
  """Set up a real-time listener for configuration changes.

  Args:
      callback (Callable[[Dict[str, Any]], None]): A function to be called when
        the configuration changes.

  Returns:
      function: A function to unsubscribe from the listener.
  """
  doc_ref = db.collection("config").document("app_config")

  def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
      logger.info("Configuration update detected")
      callback(doc.to_dict())

  return doc_ref.on_snapshot(on_snapshot)
