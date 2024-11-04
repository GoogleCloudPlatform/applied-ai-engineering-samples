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

from vertexai.language_models import CodeGenerationModel, TextGenerationModel
# from vertexai.preview.generative_models import GenerativeModel
from vertexai.generative_models import GenerativeModel, Part

def llm_generate(
    prompt: str,
    model_name: str = "text-bison",
    max_output_tokens: int = 2048,
    temperature: float = 0.0,
    top_p: float = 0.8,
    top_k: int = 40,
) -> str:
    model = TextGenerationModel.from_pretrained(model_name)
    response = model.predict(
        prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )

    return response.text


def llm_code_generate(prompt: str, model_name: str = "code-bison-32k@002") -> str:
    model = CodeGenerationModel.from_pretrained(model_name)
    parameters = {"max_output_tokens": 8192, "temperature": 0.0}

    response = model.predict(prompt, **parameters)

    return response.text


def llm_generate_gemini(prompt: str, model_name: str = "gemini-1.5-pro-001") -> str:
    model = GenerativeModel("gemini-1.5-pro-001")

    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 8192, "temperature": 0.0}
    )

    return response.text
