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


class VertexSearchRequest(BaseModel):
    search_query: str


class VertexSearchResponse(BaseModel):
    summary: str
    results: list


class VertexSearchFollowupRequest(BaseModel):
    conversation_name: str
    search_query: str


class VertexSearchFollowupResponse(BaseModel):
    conversation_name: str
    search_results: list
    message_pairs: list


class VertexRecommendRequest(BaseModel):
    document_id: str


class VertexRecommendResponse(BaseModel):
    recommended_items: list


class VertexSearchFirstConvRequest(BaseModel):
    search_query: str


class VertexSearchFirstConvResponse(BaseModel):
    conversation_name: str
    search_results: list
    message_pairs: list
