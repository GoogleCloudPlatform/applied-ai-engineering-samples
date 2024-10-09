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
"""Unit tests for the convert_to_chroma_format function in the chroma_utils module.

This module contains a series of tests designed to verify the correctness of the
convert_to_chroma_format function from the chroma_utils module. It tests various
scenarios, including simple dictionary inputs, empty dictionaries, dictionaries
with a single key-value pair, and dictionaries with multiple small key-value pairs,
to ensure the function consistently returns the expected MongoDB filter format.
"""
from datetime import datetime

from gen_ai.common.chroma_utils import convert_to_chroma_format, convert_to_vais_format


def test_convert_to_chroma_format_simple():
    """
    Tests the convert_to_chroma_format function with a simple dictionary input.

    This test ensures that the function correctly converts a dictionary containing two key-value pairs
    into the chroma format. The function is expected to return a dictionary with a single `$and` key,
    where its value is a list of dictionaries, each representing one of the input key-value pairs.

    Asserts
    -------
    The function returns the expected chroma format dictionary for a simple input case.
    """
    assert convert_to_chroma_format({"policy_number": "030500 ", "set_number": "040mcbx"}) == {
        "$and": [{"policy_number": "030500 "}, {"set_number": "040mcbx"}]
    }


def test_convert_to_chroma_format_empty():
    """
    Tests the convert_to_chroma_format function with an empty dictionary input.

    This test verifies that the function properly handles an empty input dictionary by returning a
    chroma format dictionary with an empty list associated with the `$and` key.

    Asserts
    -------
    The function returns `{"$and": []}` when given an empty dictionary as input.
    """
    assert convert_to_chroma_format({}) == {"$and": []}


def test_convert_to_chroma_format_another():
    """
    Tests the convert_to_chroma_format function with a single key-value pair input.

    This test checks if the function correctly processes a dictionary containing a single key-value
    pair, converting it into the chroma format where the `$and` key is associated with a list containing
    a single dictionary that represents the input key-value pair.

    Asserts
    -------
    The function returns the expected chroma format dictionary for an input of a dictionary with a
    single key-value pair.
    """
    assert convert_to_chroma_format({"key": "value"}) == {"$and": [{"key": "value"}]}


def test_convert_to_chroma_format_small_characters():
    """
    Tests the convert_to_chroma_format function with a dictionary containing multiple small key-value pairs.

    This test ensures that the function can handle an input dictionary with several small (one character) keys,
    correctly converting it into the chroma format. The expected output is a dictionary with the `$and` key,
    where its value is a list of dictionaries, each representing one of the input key-value pairs.

    Asserts
    -------
    The function returns the expected chroma format dictionary for a dictionary with multiple small key-value pairs.
    """
    assert convert_to_chroma_format({"a": "1", "b": "2", "c": "3"}) == {"$and": [{"a": "1"}, {"b": "2"}, {"c": "3"}]}

def test_convert_to_vais_format_empty_metadata():
    """
    Tests the convert_to_vais_format function with an empty metadata dictionary.

    This test ensures that the function correctly handles an empty input dictionary,
    returning an empty string as expected.

    Asserts
    -------
    The function returns an empty string when provided with an empty dictionary.
    """
    assert convert_to_vais_format({}) == ""

def test_convert_to_vais_format_int_value():
    """
    Tests the convert_to_vais_format function with an integer value.

    This test verifies the function's ability to correctly handle a metadata dictionary
    containing an integer value. It ensures that the function accurately converts the 
    integer value into the VAIS format, which represents the key-value pair as a string
    with an equals sign (=) separating the key and value.

    Asserts
    -------
    The function returns the expected VAIS format string for a dictionary with an integer value.
    """
    metadata = {"policy_number": 905531}
    assert convert_to_vais_format(metadata) == "policy_number = 905531"

def test_convert_to_vais_format_float_value():
    """
    Tests the convert_to_vais_format function with a float value.

    This test verifies the function's ability to correctly handle float values in the input dictionary.
    It uses a dictionary with a single key-value pair where the value is a float. The expected output
    is a string representation of the key-value pair with the float value formatted appropriately.

    Asserts
    -------
    The function returns the expected VAIS format string for a dictionary with a float value.
    """
    metadata = {"policy_number": 3.14}
    assert convert_to_vais_format(metadata) == "policy_number = 3.14"

def test_convert_to_vais_format_datetime_value():
    """
    Tests the convert_to_vais_format function with a datetime value.

    This test verifies the function's ability to correctly handle a metadata dictionary
    containing a datetime value. It ensures that the function accurately converts the
    datetime object into a string representation suitable for the VAIS format, specifically
    "YYYY-MM-DD".

    Asserts
    -------
    The function returns the expected VAIS formatted string for a dictionary with a datetime value.
    """
    metadata = {"effective_date": datetime(2024, 9, 19)}
    assert convert_to_vais_format(metadata) == 'effective_date == "2024-09-19"'

def test_convert_to_vais_format_datetime_with_operator():
    """
    Tests the convert_to_vais_format function with a datetime value and an operator.

    This test ensures that the function correctly handles a metadata dictionary where the value 
    is a datetime object and the key includes an operator (e.g., ">=", "<=", "=="). It verifies that the function
    correctly formats the datetime object as "YYYY-MM-DD" and combines it with the operator in the key.

    Asserts
    -------
    The function returns the expected VAIS format string for a datetime value with an operator.
    """
    metadata = {"effective_date >= ": datetime(2024, 9, 19)}
    assert convert_to_vais_format(metadata) == 'effective_date >= "2024-09-19"'

def test_convert_to_vais_format_string_value():
    """
    Tests the convert_to_vais_format function with a string value.

    This test ensures that the function correctly handles an input dictionary with a single key-value pair,
    where the value is a string. It verifies that the function produces the correct VAIS format string, 
    which should include the key, the 'ANY' operator, and the string value enclosed in double quotes.

    Asserts
    -------
    The function returns the expected VAIS format string for a dictionary with a string value.
    """
    metadata = {"section_name": "Policy Data"}
    assert convert_to_vais_format(metadata) == 'section_name: ANY("Policy Data")'

def test_convert_to_vais_format_multiple_values():
    """
    Tests the convert_to_vais_format function with multiple values.

    This test ensures that the function can handle a dictionary with multiple key-value pairs of different data types
    (integer, float, datetime, and string), correctly converting it into a VAIS filter expression. The expected output
    is a string with the filter expression combining all key-value pairs with the `AND` operator and appropriate
    comparison operators for each data type (`=`, `==`, `:`).

    Asserts
    -------
    The function returns the expected VAIS filter expression for a dictionary with multiple values.
    """
    metadata = {
        "policy_number": 123,
        "set_number": 3.14,
        "effective_date": datetime(2024, 9, 19),
        "section_name": "Policy Data"
    }
    expected_filter = "policy_number = 123 AND set_number = 3.14 AND effective_date == \"2024-09-19\" AND section_name: ANY(\"Policy Data\")"
    assert convert_to_vais_format(metadata) == expected_filter

def test_convert_to_vais_format_none_value():
    """
    Tests the convert_to_vais_format function with a None value.

    This test verifies the behavior of the function when encountering a key-value pair where the value is None. 
    It ensures that the function correctly handles this case and produces the expected output, which is an empty string.

    Asserts
    -------
    The function returns an empty string when the input dictionary has a value of None.
    """
    metadata = {"none_field": None}
    assert convert_to_vais_format(metadata) == ""
