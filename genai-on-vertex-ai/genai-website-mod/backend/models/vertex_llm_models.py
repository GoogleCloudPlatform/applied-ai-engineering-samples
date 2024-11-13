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

from pydantic import BaseModel


class VertexLLMRequest(BaseModel):
    prompt: str
    model_name: str = "gemini-1.5-pro-001"
    max_output_tokens: int = 1024
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 40

class VertexLLMResponse(BaseModel):
    response: str


class VertexLLMInlineTranslateRequest(BaseModel):
    selected_text: str
    target_language: str


class VertexLLMInlineTranslateResponse(BaseModel):
    response: str


class VertexTranslateRequest(BaseModel):
    prompt: dict
    target_language: str
    model_name: str = "gemini-1.5-pro-001"
    max_output_tokens: int = 2048
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 40


class VertexTranslateResponse(BaseModel):
    response: dict


class VertexLLMAIReviewRequest(BaseModel):
    webpage_body: dict
    model_name: str = "code-bison-32k@002"


class VertexLLMAIReviewResponse(BaseModel):
    modified_webpage_body: dict


class VertexLLMRefineTextRequest(BaseModel):
    selected_text: str
    instruction: str
    model_name: str = "gemini-1.5-pro-001"
    max_output_tokens: int = 2048
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 40


class VertexLLMRefineTextResponse(BaseModel):
    response: str


class VertexLLMAutocompleteRequest(BaseModel):
    paragraph_content: str
    model_name: str = "gemini-1.5-pro-001"
    max_output_tokens: int = 100
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 40


class VertexLLMAutocompleteResponse(BaseModel):
    response: str
