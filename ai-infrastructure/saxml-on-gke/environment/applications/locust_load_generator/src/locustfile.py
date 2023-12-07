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
import random
import os

from typing import Callable

from locust import HttpUser, between, task, events
from locust.runners import MasterRunner
from common import config_metrics_tracking
from common import load_test_prompts

import huggingface_hub
from transformers import LlamaTokenizer


def get_tokenizer(tokenizer_name: str) -> Callable:
    """Returns a tokenizer function based on tokenizer name."""
    tokenizer = None
    if tokenizer_name == "meta-llama/Llama-2-7b-hf":
        huggingface_hub.login(token=os.environ['HUGGINGFACE_TOKEN'])
        tokenizer = LlamaTokenizer.from_pretrained(tokenizer_name)
    return tokenizer


class FastAPIStressUser(HttpUser):
    weight = 0
    wait_time = between(0.1, 0.2)

    @task
    def test_througput(self):
        request = {
            "delay": 0.2
        }
        self.client.post("/starlette_test_throughput", json=request)


class SaxmlUser(HttpUser):
    weight = 1
    wait_time = between(0.9, 1.1)

    @task
    def lm_generate(self):
        global test_data
        global tokenizer

        if not test_data:
            logging.error("No test data configured.")
            return

        prompt = test_data[random.randint(0, len(test_data))]
        model_options = {}
        request = {
            "prompt": prompt,
            "model_id": self.environment.parsed_options.model_id,
            "model_options": model_options,
        }
        with self.client.post("/generate", json=request, catch_response=True) as resp:
            resp.request_meta["context"]["request"] = json.dumps(request)
            resp.request_meta["context"]["model_name"] = self.environment.parsed_options.model_id
            resp.request_meta["context"]["model_method"] = "Generate"
            if resp.status_code == 200:
                resp_dict = resp.json()
                resp.request_meta["context"]["model_response_time"] = resp_dict["performance_metrics"]["response_time"]
                if tokenizer:
                    resp.request_meta["context"]["tokenizer"] = self.environment.parsed_options.tokenizer
                    resp.request_meta["context"]["num_input_tokens"] = len(
                        tokenizer.encode(prompt))
                    resp.request_meta["context"]["num_output_tokens"] = sum([
                        len(tokenizer.encode(completion[0])) for completion in resp_dict["completions"]
                    ])


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--model_id", type=str, env_var="MODEL_ID",
                        include_in_web_ui=True, default="",  help="Model ID")
    parser.add_argument("--tokenizer", type=str, env_var="TOKENIZER",
                        include_in_web_ui=True, default="", help="Tokenizer to use for token calculations")
    parser.add_argument("--test_data_uri", type=str, env_var="TEST_DATA_URI",
                        include_in_web_ui=True, default="", help="GCS URI to test data")


@events.test_start.add_listener
def _(environment, **kwargs):
    if not isinstance(environment.runner, MasterRunner):
        global test_data
        global tokenizer

        logging.info(
            f"Loading test prompts from {environment.parsed_options.test_data_uri}")
        test_data = []
        test_data = load_test_prompts(environment.parsed_options.test_data_uri)
        tokenizer = get_tokenizer(environment.parsed_options.tokenizer)


@events.init.add_listener
def _(environment, **kwargs):
    logging.info("INITIALIZING LOCUST ....")
    config_metrics_tracking(environment)
