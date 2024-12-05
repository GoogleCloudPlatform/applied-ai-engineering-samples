
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from vertexai.generative_models import (
    Content,
    GenerationConfig,
    Part,
)



class ChatSession:
    """
    A simple chat session manager for interacting with a Gemini model.
    """

    def __init__(self, model, response_schema):
        """
        Initializes a new chat session.

        Args:
          model: The Gemini GenerativeModel instance.
          response_schema: The schema for the expected response.
        """
        self.model = model
        self.response_schema = response_schema
        self.history = []

    def send_message(self, message, role='user'):
        """
        Sends a message to the model and retrieves the response.

        Args:
          message: The message to send to the model.
        """
        user_message = Content(role=role, parts=[Part.from_text(message)])
        self.history.append(user_message)

        response = self.model.generate_content(
            self.history,
            generation_config=GenerationConfig(
                temperature=0, 
                top_k=1,
                top_p=0.1,
                response_mime_type="application/json",
                response_schema=self.response_schema,
            ),
        )
        # llm_message = Content(role='model', parts=[Part.from_text(response)])
        # self.history.append(llm_message)

        return response 



def start_chat(model, response_schema):
    """
    Creates a new chat session.

    Args:
      model: The Gemini GenerativeModel instance.
      response_schema: The schema for the expected response.

    Returns:
      A ChatSession instance.
    """
    return ChatSession(model, response_schema)