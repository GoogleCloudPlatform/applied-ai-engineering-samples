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

from typing import Dict, List, Optional
from pydantic import BaseModel


class ModelParams(BaseModel):
  temperature: Optional[float] = None
  max_output_tokens: Optional[int] = None
  top_p: Optional[float] = None
  top_k: Optional[int] = None

  def to_dict(self):
    return {k: v for k, v in self.dict().items() if v is not None}


class RetrieverModelPair(BaseModel):
  model_name: str
  retriever_name: str


class CompareRetrieverRequest(BaseModel):
  queries: List[str]
  retriever_model_pairs: List[RetrieverModelPair]
  index_name: str
  model_params: Dict[str, ModelParams]
  is_rerank: bool


class CompareRetrieverResponse(BaseModel):
  results: List[Dict]
