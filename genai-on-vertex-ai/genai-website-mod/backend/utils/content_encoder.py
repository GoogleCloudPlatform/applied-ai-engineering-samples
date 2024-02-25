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
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class ContentEncoder:
    def __init__(self):
        pass

    def replace_quotes(self, dictionary: dict):
        pattern = r"\""
        for key, value in dictionary.items():
            if isinstance(value, str):
                dictionary[key] = re.sub(pattern, "'", value)
            elif isinstance(value, dict):
                self.replace_quotes(value)

    def ensure_json(self, input: str) -> str:
        pattern = r"\\\""
        return re.sub(pattern, "'", input)

    def __replace_anchor_text(self, text: str) -> str:
        PATTERN_COMMENTS = r'<a href=\\"#.*?\\">((.*?))<\/a>'
        PATTERN_COMMENTS2 = r"<a href=\'#.*?\'>((.*?))<\/a>"
        PATTERN_ANNOTATION = (
            r'<span class=\\"cdx-annotation\\" data-text=\\"(.*)?\\">(.*?)</span>'
        )
        PATTERN_ANNOTATION2 = (
            r"<span class=\'cdx-annotation\' data-text=\'(.*)?\'>(.*?)</span>"
        )
        new_text = re.sub(PATTERN_COMMENTS, r"\2", text)
        new_text = re.sub(PATTERN_COMMENTS2, r"\2", new_text)
        new_text = re.sub(PATTERN_ANNOTATION, r"\2", new_text)
        new_text = re.sub(PATTERN_ANNOTATION2, r"\2", new_text)
        return new_text

    def __remove_comments(self, text: str) -> dict:
        o = json.loads(text)
        newBlocks = [b for b in o["blocks"] if b["type"] != "collaborationComment"]
        o["blocks"] = newBlocks
        return o

    def remove_comments(self, data: str) -> dict:
        removed_str = self.__replace_anchor_text(data)
        removed = self.__remove_comments(removed_str)
        return removed
