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


import json
import logging
import time
import gevent
import grpc.experimental.gevent as grpc_gevent

from datetime import datetime
from typing import Any, Dict, List, Optional
from google.pubsub_v1.types import PubsubMessage
from google.pubsub_v1.services.publisher.client import PublisherClient
from google.protobuf.json_format import MessageToDict
from google.cloud import pubsub_v1
from locust.runners import STATE_RUNNING, MasterRunner
from locust import events
from locust.env import Environment

from .metrics_pb2 import Metrics

unhandled_greenlet_exception = False
# patch grpc so that it uses gevent instead of asyncio
grpc_gevent.init_gevent()


def greenlet_exception_handler():
    """
    Returns a function that can be used as an argument to Greenlet.link_exception() to capture
    unhandled exceptions.
    """
    def exception_handler(greenlet):
        logging.error("Unhandled exception in greenlet: %s", greenlet,
                      exc_info=greenlet.exc_info)
        global unhandled_greenlet_exception
        unhandled_greenlet_exception = True
    return exception_handler


class PubsubAdapter:
    def __init__(self, env: Environment):
        if not isinstance(env.runner, MasterRunner):
            if env.parsed_options.topic_name and env.parsed_options.project_id:
                self.topic_name = env.parsed_options.topic_name
                self.project_id = env.parsed_options.project_id
                self.topic_path = f"projects/{self.project_id}/topics/{self.topic_name}"
                self.client = PublisherClient()
                self.messages = []
                self.minimum_message_queue_length = env.parsed_options.minimum_message_queue_length
                self.maximum_message_queue_length = env.parsed_options.maximum_message_queue_length
                self.publisher_sleep_time = env.parsed_options.publisher_sleep_time
                self.request_handler = None
                self.test_id = None
                self.environment = env
                env.events.test_start.add_listener(self.on_test_start)

            else:
                logging.warning(
                    'No Pubsub topic configured. Metrics will not be tracked. To enable tracking you must set --topic_name and --project_id parameters.')

    def on_test_start(self, environment, **kwargs):
        """Registers the request handler and starts the publishing greenlet."""

        self.test_id = None
        if not isinstance(environment.runner, MasterRunner):
            # Remove any previously registered request handler
            if self.request_handler:
                environment.events.request.remove_listener(
                    self.request_handler)
                self.request_handler = None

            if environment.parsed_options.metrics_tracking == "enabled":
                if environment.parsed_options.test_id:
                    self.test_id = environment.parsed_options.test_id
                    logging.info("Adding request listener")
                    self.request_handler = environment.events.request.add_listener(
                        self.log_request)
                    logging.info("Spawning a publishing greenlet")
                    gevent.spawn(self.publisher, self.publisher_sleep_time).link_exception(
                        greenlet_exception_handler())
                else:
                    logging.warning(
                        "Test ID not set. Metrics tracking disabled.")
            else:
                logging.info("Metrics tracking disabled by a user")

    def publisher(self, sleep_time=1):
        """This function is executed by a publishing greenlet

           It awakens every configured seconds and publishes 
           accumulated metrics to a configured Pubsub topic.
        """
        logging.info("Entering the Pubsub publishing greenlet")
        logging.info("Waiting for the runner to start")
        while self.environment.runner.state != STATE_RUNNING:
            gevent.sleep(1)
            continue
        logging.info("The runner has starterd.")
        while self.environment.runner.state == STATE_RUNNING:
            gevent.sleep(sleep_time)
            self.publish_messages()
        logging.info("The runner has stopped.")
        self.publish_messages()
        logging.info("Exiting the Pubsub publishing greenlet.")

    def publish_messages(self):
        """Publishes all metrics messages in a message queue."""

        if len(self.messages) >= self.minimum_message_queue_length:
            try:
                start_time = time.time()
                self.client.publish(topic=self.topic_path,
                                    messages=self.messages)
                total_time = int((time.time() - start_time) * 1000)
                logging.info(
                    f"Published {len(self.messages)} request records to {self.topic_path} in {total_time} miliseconds")
                self.messages = []
            except Exception as e:
                logging.error(
                    f"Exception when publishing request records - {e}")

    def log_request(self,
                    request_type: str,
                    name: str,
                    response_time: int,
                    response_length: int,
                    response: object,
                    context: dict,
                    exception: Exception,
                    start_time: datetime,
                    **kwargs):
        """This is an event handler for Locust on_request events.
           It prepares a metric proto buffer and appends it to a message queue.
        """

        if not self.test_id:
            logging.warning(
                "Test ID NOT configured. The message will not be tracked.")
            return

        if len(self.messages) > self.maximum_message_queue_length:
            logging.warning(
                f"Maximum number of request records queued - {len(self.messages)}. Removing the oldest record")
            self.messages.pop()

        message = self._prepare_message(
            test_id=self.test_id,
            request_type=request_type,
            name=name,
            response_time=response_time,
            response_length=response_length,
            response=response,
            context=context,
            exception=exception,
            start_time=start_time)

        self.messages.append(message)

    def _prepare_message(self,
                         test_id: str,
                         request_type: str,
                         name: str,
                         response_time: int,
                         response_length: int,
                         response: object,
                         context: dict,
                         exception: Exception,
                         start_time: datetime):
        """Prepare a metrics protobuf."""

        metrics = {
            "test_id": test_id,
            "request_type": request_type,
            "request_name": name,
            "response_time": response_time,
            "response_length": response_length,
            "start_time": time.strftime(
                "%Y-%m-%d %H:%M:%S",  time.localtime(start_time))
        }
        if exception:
            metrics["exception"] = str(exception)
        if self.environment.parsed_options.request_response_logging == "enabled":
            response_dict = response.json()
            metrics["response"] = json.dumps(response_dict)

        if context:
            for key in ["model_name", "model_method", "request", "num_input_tokens", "num_output_tokens", "tokenizer", "model_response_time"]:
                value = context.get(key)
                if value:
                    metrics[key] = value

        metrics_proto = Metrics(**metrics)
        message = PubsubMessage(data=json.dumps(
            MessageToDict(metrics_proto)).encode("utf-8"))

        return message


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--metrics_tracking", include_in_web_ui=True, choices=["enabled", "disabled"], default="enabled",
                        help="Whether to publish metrics to Pubsub topic")
    parser.add_argument("--request_response_logging", include_in_web_ui=True, choices=["enabled", "disabled"], default="enabled",
                        help="Whether to include request and response content in published metrics")
    parser.add_argument("--test_id", type=str,
                        include_in_web_ui=True, default="", help="Test ID")
    parser.add_argument("--topic_name", type=str, env_var="TOPIC_NAME",
                        include_in_web_ui=False, default="",  help="Pubsub topic name")
    parser.add_argument("--project_id", type=str, env_var="PROJECT_ID",
                        include_in_web_ui=False, default="",  help="Project ID")
    parser.add_argument("--maximum_message_queue_length", type=int, env_var="MAXIMUM_MESSAGE_QUEUE_LENGTH",
                        include_in_web_ui=False, default=1000, help="The maximum size of the in-memory message queue that stages messages for publishing")
    parser.add_argument("--minimum_message_queue_length", type=int, env_var="MINIMUM_MESSAGE_QUEUE_LENGTH",
                        include_in_web_ui=False, default=10, help="The batch of messages will be published after the length of the in-memory message queue goes over this threshold")
    parser.add_argument("--publisher_sleep_time", type=int, env_var="PUBLISHER_SLEEP_TIME",
                        include_in_web_ui=False, default=2, help="Message publishing interval in seconds")
