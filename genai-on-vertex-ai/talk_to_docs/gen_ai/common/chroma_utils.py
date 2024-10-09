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
"""Provides utilities for converting data to Chroma-specific MongoDB filter formats.

This module includes functions designed to facilitate the conversion of standard
Python dictionaries into MongoDB filter formats. It is particularly focused on
creating MongoDB query filters using the "$and" operator from given dictionaries,
enabling dynamic construction of database queries based on variable criteria.

The main utility function, `convert_to_chroma_format`, accepts a dictionary where
each key-value pair represents a specific query condition. It then converts this
into a format suitable for use with MongoDB queries, aiding in the seamless integration
of application-level data structures with database-level querying capabilities.
"""

from typing import Any
from datetime import datetime


def convert_to_chroma_format(metadata: dict[str, str]) -> dict[str, dict[str, str]]:
    """
    Converts a dictionary into a MongoDB filter format with "$and" operator.

    Args:
        input_dict (dict): A dictionary where each key-value pair represents a field and its value.

    Returns:
        dict: A MongoDB filter object using the "$and" operator with the given field-value pairs.

    Example:
        >>> dict_to_mongo_filter({"policy_number": "030500 ", "set_number": "040mcbx"})
        {'$and': [{'policy_number': '030500 '}, {'set_number': '040mcbx'}]}
    """
    return {"$and": [{k: v} for k, v in metadata.items()]}


def convert_to_vais_format(metadata: dict[str, str]) -> str:
    """
    Converts a metadata dictionary into a Vertex AI Search filter string,
    focusing on "is" equality conditions.

    Args:
        metadata (dict): The metadata dictionary to convert.

    Returns:
        str: The generated search filter string.
    """
    filters = []
    for key, value in metadata.items():
        if value:
            if isinstance(value, (int, float)):
                filters.append(f"{key} = {value}")
            elif isinstance(value, bool):
                filters.append(f'{key} = "{str(value).lower()}"')
            elif isinstance(value, datetime):
                if len(key.split()) == 1:
                    filters.append(f'{key} == "{value.strftime("%Y-%m-%d")}"')
                elif len(key.split()) == 2:
                    dt_key, operator = key.split()
                    filters.append(f'{dt_key} {operator} "{value.strftime("%Y-%m-%d")}"')
            else:
                filters.append(f'{key}: ANY("{value}")')

    return " AND ".join(filters)


def map_composite_to_dict(map_composite: Any) -> dict[Any, Any]:
    """Converts a Protobuf MapComposite object into a standard Python dictionary.

    This function iterates over the key-value pairs in the `MapComposite` and adds them to
    a new dictionary, which is then returned.

    Args:
        map_composite: The Protobuf MapComposite object to convert.

    Returns:
        Dict[Any, Any]: A Python dictionary containing the same key-value pairs
            as the input MapComposite.

    Example:
        map_comp = my_message.my_map_field
        data_dict = map_composite_to_dict(map_comp)
    """
    result = {}
    for key, value in map_composite.items():
        result[key] = value
    return result
