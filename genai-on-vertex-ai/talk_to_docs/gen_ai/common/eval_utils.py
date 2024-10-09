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
"""This module provides functions for evaluating model answers."""

from gen_ai.common.ioc_container import Container
import json5


def enhance_question(question: str, enhanced_string: str) -> str:
    """Enhances the question with the provided string as determined in enhanced_prompt.

    Args:
        question: The question to enhance.
        enhanced_string: The string to enhance the question with.

    Returns:
        The enhanced question.
    """
    enhance_question_chain = Container.enhance_question_chain
    enhanced_question = enhance_question_chain().run(
        question=question,
        member_context=enhanced_string,
    )
    enhanced_question = eval(enhanced_question)  # pylint: disable=eval-used
    enhanced_question = enhanced_question["appended_question_with_member_context"]
    return enhanced_question


def golden_scoring_answer(question: str, expected_answer: str, actual_answer: str) -> int:
    """Checks how good is the answer for the question.

    Args:
        question: The question asked.
        expected_answer: The expected answer.
        actual_answer: The actual answer.

    Returns:
        Correctness score.
    """
    golden_answer_scoring_chain = Container.golden_answer_scoring_chain
    json_corrector_chain = Container.json_corrector_chain
    output_raw = golden_answer_scoring_chain().run(
        question=question,
        expected_answer=expected_answer,
        actual_answer=actual_answer,
    )
    try:
        output_raw = output_raw.replace("```json", "").replace("```", "")
        output = json5.loads(output_raw)
    except Exception:  # pylint: disable=W0718
        json_output = json_corrector_chain().run(json=output_raw)
        json_output = json_output.replace("```json", "").replace("```", "")
        output = json5.loads(json_output)

    return int(output["correctness_score"])


def substring_matching(left_string: str, right_string: str) -> int:
    """Checks how good much of left string is contained in right string.

    Args:
        left_string: Left string.
        right_string: Right string.

    Returns:
        Score of how much of left string is contained in right string.
    """
    string_matcher_chain = Container.string_matcher_chain
    json_corrector_chain = Container.json_corrector_chain
    output_raw = string_matcher_chain().run(left_string=left_string, right_string=right_string)
    try:
        output_raw = output_raw.replace("```json", "").replace("```", "")
        output = json5.loads(output_raw)
    except Exception:  # pylint: disable=W0718
        json_output = json_corrector_chain().run(json=output_raw)
        json_output = json_output.replace("```json", "").replace("```", "")
        output = json5.loads(json_output)

    return int(output["left_in_right_score"])
