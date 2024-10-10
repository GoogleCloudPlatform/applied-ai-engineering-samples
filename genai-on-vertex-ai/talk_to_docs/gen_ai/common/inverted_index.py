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
"""This module provides the invered index that we use for retrieving metadata"""
class InvertedIndex:
    def build_map(self, docs):
        doc_mapping = {}
        for plan, documents in docs.items():
            texts = [x.page_content for x in documents]
            metadatas = [x.metadata for x in documents]
            docs_plan = {f"{plan}_{i}": (x, y) for i, (x, y) in enumerate(zip(texts, metadatas))}
            doc_mapping.update(docs_plan)
        return doc_mapping
