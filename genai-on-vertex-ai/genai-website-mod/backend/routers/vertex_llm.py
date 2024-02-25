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

import json
import tomllib as toml

from fastapi import APIRouter, HTTPException
from models.vertex_llm_models import (
    VertexLLMAIReviewRequest,
    VertexLLMAIReviewResponse,
    VertexLLMAutocompleteRequest,
    VertexLLMAutocompleteResponse,
    VertexLLMInlineTranslateRequest,
    VertexLLMInlineTranslateResponse,
    VertexLLMRefineTextRequest,
    VertexLLMRefineTextResponse,
    VertexLLMRequest,
    VertexLLMResponse,
    VertexTranslateRequest,
    VertexTranslateResponse,
)
from utils.vertex_llm_utils import llm_code_generate, llm_generate, llm_generate_gemini

with open("./config.toml", "rb") as f:
    config = toml.load(f)

translate_prompt = config["vertex-llm"]["translate_prompt"]
ai_review_prompt = config["vertex-llm"]["ai_review_prompt"]
ai_refine_prompt = config["vertex-llm"]["ai_refine_prompt"]
ai_translate_inline_prompt = config["vertex-llm"]["ai_translate_inline_prompt"]

router = APIRouter()


@router.post("/vertex_llm")
def vertex_llm_call(data: VertexLLMRequest) -> VertexLLMResponse:
    try:
        response = llm_generate(
            prompt="translate to hindi: " + data.prompt,
        )

    except Exception as e:
        print(f"ERROR: Vertex LLM error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return VertexLLMResponse(response=response)


@router.post(path="/ai_refine_text")
def ai_refine_text(data: VertexLLMRefineTextRequest) -> VertexLLMRefineTextResponse:
    try:
        final_prompt = f"{ai_refine_prompt} {data.selected_text} \n REFINE_PROMPT: \n {data.instruction}"
        print(final_prompt)
        response = llm_generate(
            final_prompt,
            model_name=data.model_name,
            max_output_tokens=data.max_output_tokens,
            temperature=data.temperature,
            top_p=data.top_p,
            top_k=data.top_k,
        )

        print(response)
    except Exception as e:
        print(f"ERROR: Vertex LLM error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return VertexLLMRefineTextResponse(response=response)


@router.post(path="/ai_translate_webpage")
def ai_translate_webpage(data: VertexTranslateRequest) -> VertexTranslateResponse:
    try:
        final_prompt = f"{translate_prompt}\n {data.target_language} \n {json.dumps(data.prompt)} \n OUTPUT: "

        response = llm_generate(
            final_prompt,
            model_name=data.model_name,
            max_output_tokens=data.max_output_tokens,
            temperature=data.temperature,
            top_p=data.top_p,
            top_k=data.top_k,
        )

    except Exception as e:
        print(f"ERROR: Vertex LLM error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return VertexTranslateResponse(response=json.loads(response))


@router.post(path="/ai-review")
def webpage_ai_review(data: VertexLLMAIReviewRequest) -> VertexLLMAIReviewResponse:
    try:
        final_prompt = f"{ai_review_prompt}{json.dumps(data.webpage_body)} \n AI SUGGESTION ENHANCED MODIFIED OUTPUT: \n"  # noqa: E501
        print(final_prompt)

        if data.model_name == "text-bison-32k@002":
            print("text-bison-32k@002")
            response = llm_generate(prompt=final_prompt)

        if data.model_name == "code-bison-32k@002":
            print("code-bison-32k@002")
            response = llm_code_generate(prompt=final_prompt)

        if data.model_name == "gemini-pro":
            print("gemini-pro")
            response = llm_generate_gemini(prompt=final_prompt)

        print(json.dumps(response, indent=4))

    except Exception as e:
        print(f"ERROR: Vertex LLM error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return VertexLLMAIReviewResponse(modified_webpage_body=json.loads(response))


@router.post(path="/ai-autocomplete")
def ai_autocomplete(
    data: VertexLLMAutocompleteRequest,
) -> VertexLLMAutocompleteResponse:
    try:
        final_prompt = f"You are an expert writer. Complete the following paragraph: {data.paragraph_content}"

        response = llm_generate(
            final_prompt,
            model_name=data.model_name,
            max_output_tokens=data.max_output_tokens,
            temperature=data.temperature,
            top_p=data.top_p,
            top_k=data.top_k,
        )

    except Exception as e:
        print(f"ERROR: Vertex LLM error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return VertexLLMAutocompleteResponse(response=response)


@router.post(path="/ai-translate-inline")
def ai_translate_inline(
    data: VertexLLMInlineTranslateRequest,
) -> VertexLLMInlineTranslateResponse:
    try:
        final_prompt = f"{ai_translate_inline_prompt} {data.selected_text} \n TARGET_LANGUAGE: \n {data.target_language}"  # noqa: E501
        response = llm_generate(
            final_prompt,
        )
    except Exception as e:
        print(f"ERROR: Vertex LLM error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return VertexLLMRefineTextResponse(response=response)
