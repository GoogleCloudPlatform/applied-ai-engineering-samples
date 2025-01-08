# noqa: E231

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

import tomllib

from vertexai.generative_models import GenerativeModel, SafetySetting, Part
from fastapi import APIRouter
from models.vertex_llm_video_models import (
    VertexLLMVideoChatRequest,
    VertexLLMVideoResponse,
)
from google.cloud.aiplatform import telemetry
from utils.consts import USER_AGENT

with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

router = APIRouter()

@router.post(path="/api/video-chat")
def video_chat(req: VertexLLMVideoChatRequest) -> VertexLLMVideoResponse:
    print(f"video_chat:{req}")
    generation_config = {
        "max_output_tokens": req.max_output_tokens,
        "temperature": req.temperature,
        "top_p": req.top_p,
        "top_k": req.top_k
    }
    model = GenerativeModel(
        req.model_name,
        generation_config=generation_config,

    )
    
    if req.conversation_logs is not None and len(req.conversation_logs) > 0:
        try:
            history = [
                {
                    "role": log["role"],
                    "parts": log["parts"]
                } for log in req.conversation_logs]
        except Exception as err:
            print(f"[Error]Error parsing conversation log:{err}")
            history = None
    else:
        history = None

    with telemetry.tool_context_manager(USER_AGENT):
        chat = model.start_chat(history=history)
        video1 = Part.from_uri(
            mime_type="video/mp4",
            uri=req.video_url,
        )
        print (f"video1: {video1}")
        print (f"prompt: {req.prompt}")
        try:
            resp = chat.send_message(
                [video1, req.prompt]
            )
        except Exception as error:
            print(f"[Error]{error}")
            return VertexLLMVideoResponse(response="Something went wrong, please try again later.")
        return VertexLLMVideoResponse(response=resp.text)
