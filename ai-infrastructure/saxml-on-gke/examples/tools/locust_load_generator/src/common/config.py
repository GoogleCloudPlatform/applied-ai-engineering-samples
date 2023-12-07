
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import jsonlines
import re
import gevent

from google.cloud import storage

from locust import events
from locust.runners import MasterRunner, WorkerRunner
from common import PubsubAdapter


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global test_data
    global test_id
    global pubsub_adapter

    logging.info("INITIALIZING LOCUST ....")
    if not isinstance(environment.runner, MasterRunner):
        if environment.parsed_options.topic_name and environment.parsed_options.project_id:
            topic_path = f"projects/{environment.parsed_options.project_id}/topics/{environment.parsed_options.topic_name}"
            logging.info(
                f'Registering PubsubAdapter for topic: {topic_path}.')
            pubsub_adapter = PubsubAdapter(environment=environment,
                                           topic_path=topic_path,
                                           batch_size=environment.parsed_options.message_buffer_size)
        else:
            pubsub_adapter = None
            logging.info(
                'No Pubsub topic configured. User requests will NOT be tracked. To enable tracking you must set --topic_name and --project_id parameters.')


@events.test_start.add_listener
def _(environment, **kwargs):
    global test_data
    global test_id
    global pubsub_adapter

    test_data = []
    test_id = environment.parsed_options.test_id

    if not isinstance(environment.runner, MasterRunner):
        try:
            # Try loading test data
            test_data_uri = environment.parsed_options.test_data
            gcs_uri_pattern = "^gs:\/\/[a-z0-9.\-_]{3,63}\/(.+\/)*(.+)$"
            if not test_data_uri:
                raise ValueError("Test data URI not provided")
            if not re.match(gcs_uri_pattern, test_data_uri):
                raise ValueError(f"Incorrect GCS URI: {test_data_uri}")

            client = storage.Client()
            bucket_name = environment.parsed_options.test_data.split('/')[2]
            blob_name = "/".join(
                environment.parsed_options.test_data.split('/')[3:])
            bucket = client.get_bucket(bucket_name)
            blob = storage.Blob(blob_name, bucket)
            data_file_name = '/tmp/data.jsonl'
            with open(data_file_name, 'wb') as f:
                blob.download_to_file(f)
            test_data = []
            with jsonlines.open(data_file_name) as reader:
                for obj in reader:
                    test_data.append(obj['input'])

            logging.info(f"Loaded {len(test_data)} test prompts.")

            if test_id and pubsub_adapter:
                logging.info("Registering request listener")
                pubsub_adapter.request_handler = environment.events.request.add_listener(pubsub_adapter.log_request)
                logging.info("Spawning Pubsub publishing greenlet")
                pubsub_adapter.test_id = test_id
                gevent.spawn(pubsub_adapter.flusher, ).link_exception(
                    greenlet_exception_handler())
            else:
                logging.warning(
                    "Could not configure Pubsub publishing. Requests will not be tracked.")

        except Exception as e:
            logging.error(f"Error loading test data: {e}. Stopping the runner")
            test_data = []
            environment.runner.quit()


@events.test_stop.add_listener
def _(environment, **kwargs):
    global pubsub_adapter
    global test_id

    if not isinstance(environment.runner, MasterRunner):
        if pubsub_adapter:
                logging.info(
                    f"Flushing the remaining messages as the test was stopped")
                pubsub_adapter.flush_messages(force=True)
                if pubsub_adapter.request_handler:
                    logging.info(
                        f"Removing the request handler")
                    environment.events.request.remove_listener(pubsub_adapter.request_handler)


@events.init_command_line_parser.add_listener
def _(parser):

    parser.add_argument("--model_id", type=str,
                        include_in_web_ui=True, default="", help="Model ID")
    parser.add_argument("--test_id", type=str,
                        include_in_web_ui=True, default="", help="Test ID")
    parser.add_argument("--topic_name", type=str, env_var="TOPIC_NAME",
                        include_in_web_ui=False, default="",  help="Pubsub topic name")
    parser.add_argument("--project_id", type=str, env_var="PROJECT_ID",
                        include_in_web_ui=False, default="",  help="Project ID")
    parser.add_argument("--test_data", type=str, env_var="TEST_DATA",
                        include_in_web_ui=True, default="", help="GCS URI to test data")
    parser.add_argument("--message_buffer_size", type=int, env_var="MESSAGE_BUFFER_SIZE",
                        include_in_web_ui=False, default=25, help="The size of the batch for Pubsub transactions")
    parser.add_argument("--metrics_tracking", include_in_web_ui=True, choices=["enabled", "disabled"] default="enabled",
                        help="Whether to publish metrics to Pubsub topic")
    parser.add_argument("--query_response_logging", include_in_web_ui=True, choices=["enabled", "disabled"], default="enabled",
                        help="Whether to include request and response content in published metrics")
