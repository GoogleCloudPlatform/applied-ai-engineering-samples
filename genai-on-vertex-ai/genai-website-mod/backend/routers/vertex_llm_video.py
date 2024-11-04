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

with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

router = APIRouter()

@router.post(path="/api/video-chat")
def video_chat(req: VertexLLMVideoChatRequest) -> VertexLLMVideoResponse:

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
        history = [
            {
                "role": log["role"],
                "parts": log["parts"]
            } for log in req.conversation_logs]
    else:
        history = None
        # history=[
        #         {"role": "user", "parts": "Hello"},
        #         {"role": "model", "parts": "Great to meet you. What would you like to know?"},
        #     ]
        
    chat = model.start_chat(history=history)
    video1 = Part.from_uri(
        mime_type="video/mp4",
        uri=req.video_url,
        # safety_settings=safety_settings
    )
    print (f"video1: {video1}")
    print (f"pronmpt: {req.prompt}")
    resp = chat.send_message(
        [video1, req.prompt]
    )
    return VertexLLMVideoResponse(response=resp.text)
