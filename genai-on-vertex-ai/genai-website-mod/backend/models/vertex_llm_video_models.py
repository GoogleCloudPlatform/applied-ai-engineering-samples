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


class VertexLLMVideoChatRequest(BaseModel):
    prompt: str
    video_url: str
    model_name: str = "gemini-1.5-pro-001"
    max_output_tokens: int = 8192
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 40
    conversation_logs: list[dict] = None



class VertexLLMVideoResponse(BaseModel):
    response: str
