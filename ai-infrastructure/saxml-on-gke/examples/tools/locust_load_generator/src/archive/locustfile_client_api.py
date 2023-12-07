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

import os
import json
import random
import time

import huggingface_hub
import jsonlines
import sax

from locust import User, task, between

from locust.runners import MasterRunner, WorkerRunner, LocalRunner
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, STATE_RUNNING

from transformers import LlamaTokenizer

import locust.runners
locust.runners.HEARTBEAT_LIVENESS = 90 
locust.runners.HEARBEAT_INTERVAL = 1 




LOG_STATS_INTERVAL_SEC = 5
LOG_NAME = 'locust'


def lm_generate_task(
        user:object,
        model:str,
):
    """
    Calls lm.Generate method on the model.
    """

    elapsed_time = 100 + random.randint(1,50)
    output_tokens = 50 + random.randint(1, 50)
    simulate_exception = random.randint(1, 10)

    exception = None
    if simulate_exception > 9:
        exception = RuntimeError('Something went wrong')
 
    user.environment.events.request.fire(
        request_type=f'lm.generate',
        name=model,
        response_time=elapsed_time,
        response_length=output_tokens,
        exception=exception 
    )

class SaxmlUser(User):
    """
    A class simulating calls to Saxml model servers.
    """

    def __init__(self, environment):
        super().__init__(environment)

    
    wait_time = between(0.2, 0.3)
    #wait_time =1

    def on_start(self):

        self.model_id='/sax/test/llama7bfp16tpuv5e'
        tokenizer = "meta-llama/Llama-2-7b-hf"

        huggingface_hub.login(token=os.environ['HUGGINGFACE_TOKEN'])
        self.tokenizer = LlamaTokenizer.from_pretrained(tokenizer)
        self.model = sax.Model(self.model_id)
        self.lm_model = self.model.LM()

        self.model_options = sax.ModelOptions()
        self.model_options.SetExtraInput("per_example_max_decode_steps", 128)

        self.prompts = [
            'Who is Harry Potter?',
            'What is your name?'
        ]

        self.first_prompt_index = 0
        self.last_prompt_index = 1
        
#        self.tasks.clear()
#        task = partial(lm_generate_task,
#                       model='llama7b')
#        update_wrapper(task, lm_generate_task) 
#
#        self.tasks.append(task)
#
#    def on_stop(self):
#        self.tasks.clear()

    @task
    def lm_generate(self):
        """
        Calls lm.Generate method on the model.
        """

        elapsed_time = 100 + random.randint(1,50)
        output_tokens = 50 + random.randint(1, 50)
        simulate_exception = random.randint(1, 10)
        prompt_id = random.randint(self.first_prompt_index, self.last_prompt_index)
        prompt = self.prompts[prompt_id]

        num_prompt_tokens = len(self.tokenizer.encode(prompt))

        start_time = time.time() 
        prediction = self.lm_model.Generate(prompt, self.model_options)
        elapsed_time = int((time.time() - start_time) * 1000)

        num_output_tokens = len(self.tokenizer.encode(prediction[0][0]))

        exception = None
        if  num_output_tokens == 0:
            exception = RuntimeError('Empty response')
    
        self.environment.events.request.fire(
            request_type=f'lm.generate',
            name=self.model_id,
            response_time=elapsed_time,
            response_length=output_tokens,
            exception=exception 
        )
