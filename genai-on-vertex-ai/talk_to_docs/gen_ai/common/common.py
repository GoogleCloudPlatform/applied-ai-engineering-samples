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
"""
This module provides utility functions for the Gen AI project, including token 
counting, data loading, JSON handling, and interaction with language models.
"""

import json
import re
import os
import warnings
from typing import List, Tuple

import tiktoken
import yaml
from langchain.chat_models import ChatVertexAI
from langchain.chat_models.base import BaseChatModel
from langchain.llms import VertexAI
from langchain.schema import Document

from gen_ai.deploy.model import QueryState

warnings.filterwarnings("ignore", category=DeprecationWarning)

LLM_YAML_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "llm.yaml")


class TokenCounter:
    """
    A utility class for counting the number of tokens in a given text.
    This class supports different models for token counting, including
    models specified as "bison" or "gemini", which use a model-specific
    token counting function. For other models, a generic token counting
    approach based on the tiktoken library is used.
    """

    def __init__(self, model_name):
        """
        Initializes the TokenCounter object.
        If the name contains "bison", LangChain's "get_num_tokens" is loaded.
        Otherwise, "get_num_tokens_from_string_chatgpt" method is loaded, which
        is implemented on base of tiktoken.

        Args:
            model_name (str): The name of the model to use for token counting

        """
        if "bison" in model_name or "gemini" in model_name:
            llm = get_or_create_model(model_name)
            self.counting_fn = llm.get_num_tokens
        else:
            self.counting_fn = self.get_num_tokens_from_string_chatgpt

    def get_num_tokens_from_string(self, text: str) -> int:
        """Estimate token count for the given text.

        Args:
            text (str): Prompt text

        Returns:
            int: Estimated token count
        """
        return self.counting_fn(text)

    def get_num_tokens_from_string_chatgpt(self, text: str) -> int:
        """Estimate token count for the given text using tiktoken.

        Args:
            text (str): Prompt text

        Returns:
            int: Estimated token count
        """
        encoding_name = "cl100k_base"
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens


token_counter = None


def provide_token_counter() -> TokenCounter:
    """Create token counter object based on TokenCounter class.
    Parameters:
        model_name: The name of the model based on which to count tokens.
    Returns:
        TokenCounter object.
    """
    config = load_yaml(LLM_YAML_FILE)
    return TokenCounter(config["model_name"])


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file)


def load_yaml(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


llms = {}


def get_or_create_model(model_name: str) -> BaseChatModel:
    """Create a language model based on the model name.
    Parameters:
        model_name: The name of the model to create.
    Returns:
        The created model.
    """
    global llms  # pylint: disable=W0602
    if model_name in llms:
        return llms[model_name]
    config = load_yaml(LLM_YAML_FILE)
    temperature = config.get("temperature", 0.001)
    max_output_tokens = config.get("max_output_tokens", 4000)
    if "gemini" in model_name or "unicorn" in model_name:
        llms[model_name] = VertexAI(model_name=model_name, temperature=temperature,
                                     max_output_tokens=max_output_tokens, seed=42)
        return llms[model_name]
    elif "chat-bison" in model_name or "text-bison" in model_name:
        llms[model_name] = ChatVertexAI(
            model_name=model_name, temperature=temperature, max_output_tokens=max_output_tokens
        )
        return llms[model_name]
    else:
        raise ValueError("Unknown model name")


def roman_to_decimal(roman: str) -> str:
    res = 0
    i = 0

    roman_dict = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    while i < len(roman):

        # Getting value of symbol s[i]
        s1 = roman_dict[roman[i]]

        if i + 1 < len(roman):

            # Getting value of symbol s[i + 1]
            s2 = roman_dict[roman[i + 1]]

            # Comparing both values
            if s1 >= s2:

                # Value of current symbol is greater
                # or equal to the next symbol
                res = res + s1
                i = i + 1
            else:

                # Value of current symbol is greater
                # or equal to the next symbol
                res = res + s2 - s1
                i = i + 2
        else:
            res = res + s1
            i = i + 1

    return str(res)


def custom_extract_data(content: str) -> Document:
    """
    Extract section number, and section name from the content. The section
    number and name are used as metadata in the Document object. Return the created document object.
    """
    lines = content.split("\n\n")

    parameter_one, *others = lines[0].split("---")
    if others:
        metadata = {"section_number": parameter_one, "section_name": others[0]}
    else:
        metadata = {"term_name": parameter_one}

    document = Document(page_content=content, metadata=metadata)

    return document


def default_extract_data(content: str) -> Document:
    """
    This is default extraction logic for woolies.
    Extract section number, and section name from the content and omits term_name. The section
    number and name are used as metadata in the Document object. Return the created document object.
    """

    return Document(page_content=content)


def remove_duplicates(docs):
    unq = []
    for doc in docs:
        if doc not in unq:
            unq.append(doc)
    return unq


def word_count(s: str) -> int:
    return len(re.findall(r"\w+", s))


def split_large_document(document: str, threshold: int) -> List[Tuple[str, int]]:
    """
    Splits a large document into smaller pieces without splitting sentences and
    adjusts the threshold to account for a conversion from words to tokens.

    This function takes a document as a string and a threshold for the maximum number of words
    allowed in each piece. It first adjusts the threshold to create a conservative estimate
    of words to tokens, assuming that 100 words produce about 130 tokens. The document is then
    split into sentences, and these sentences are grouped into pieces that do not exceed the
    adjusted word count threshold. Each piece is a continuous segment of the original document,
    ensuring that sentences are not split across different pieces.

    Args:
        document (str): The document to be split into pieces.
        threshold (int): The word count threshold for each piece, before adjusting for the
                         conversion from words to tokens.

    Returns:
        List[Tuple[str, int]]: A list of tuples where each tuple contains a piece of the document
                               as a string and the length of that piece in terms of the number of
                               characters. The threshold adjustment reduces the risk of exceeding
                               token limits when processing the text further.

    Note:
        The threshold adjustment is based on an estimated conversion rate from words to tokens,
        which may vary depending on the actual content of the document. This conservative
        adjustment helps in avoiding exceeding token limits in subsequent processing stages.

    Example:
        >>> document = "This is the first sentence. Here goes the second one. And another sentence follows."
        >>> threshold = 20  # Before adjustment for tokens
        >>> split_large_document(document, threshold)
        [('This is the first sentence. Here goes the second one.', 55),
         ('And another sentence follows.', 28)]
    """
    threshold = threshold / 1  # 1.3 conservative bound for words -> tokens (100 words produce about 130 tokens)

    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", document)

    current_count = 0
    current_piece = []
    pieces = []

    for sentence in sentences:
        sentence_word_count = word_count(sentence)
        if current_count + sentence_word_count > threshold and current_piece:
            pieces.append(" ".join(current_piece))
            current_piece = [sentence]
            current_count = sentence_word_count
        else:
            current_piece.append(sentence)
            current_count += sentence_word_count

    if current_piece:
        pieces.append(" ".join(current_piece))

    return [(x, len(x)) for x in pieces]


def merge_outputs(outputs):
    """
    Merges a list of outputs based on their confidence scores. If any output has a confidence score of 100,
    it is returned immediately. Otherwise, outputs are merged based on specific rules for different keys.

    Args:
        outputs (list of tuple): A list where each element is a tuple containing an output dictionary and a
                                 confidence score (int).

    Returns:
        tuple: A tuple containing the merged output dictionary, the highest confidence score among the outputs,
               and the index of the output with the highest confidence score.

    Note:
        - "plan_and_summaries" and "additional_sections_to_retrieve" are concatenated.
        - "context_used" is extended if not empty, otherwise replaced.
        - "answer" is updated to the one with the highest confidence score.
    """
    if not outputs:
        return None, 0, -1

    highest_confidence_output = outputs[0][0]
    highest_confidence_score = outputs[0][1]
    highest_confidence_index = 0

    if highest_confidence_score == 100:
        return highest_confidence_output, highest_confidence_score, highest_confidence_index

    for index, (output, score) in enumerate(outputs[1:]):
        if score == 100:
            return output, score, index + 1

        for key, value in output.items():
            if key in ["plan_and_summaries", "additional_sections_to_retrieve"]:
                highest_confidence_output[key] += value
            elif key == "context_used":
                if isinstance(highest_confidence_output[key], str):
                    highest_confidence_output[key] = value
                else:
                    highest_confidence_output[key].extend(value if isinstance(value, list) else [value])
            elif key == "answer" and score > highest_confidence_score:
                highest_confidence_output[key] = value
                highest_confidence_score = score
                highest_confidence_index = index + 1

    return highest_confidence_output, highest_confidence_score, highest_confidence_index


def update_used_docs(used_articles: List[Tuple[str, int]], query_state: QueryState) -> List[Tuple[str, int]]:
    """
    Updates and sorts a list of used documents based on a query state, prioritizing documents required by the state.

    This method filters and sorts articles based on their relevance and the requirements specified in the query state.
    If the query state indicates that all sections are needed, it identifies which documents from the `used_articles`
    list are also listed in the `query_state['all_sections_needed']`, combines them with the missing articles
    specified in the query state, and then sorts the list of articles by their relevancy score in descending order.

    Parameters:
    - used_articles (List[Tuple[str, int]]): A list of tuples where each tuple contains a document filename (str) and
      its relevancy score (int) to the query.
    - query_state (QueryState): A QueryState object representing the state of the query, potentially including a key
      'all_sections_needed' which is a list of tuples. Each tuple in this list contains a document filename (str) and
      its relevancy score (int) required for the current query.

    Returns:
    - List[Tuple[str, int]]: A list of tuples, where each tuple contains a document filename and its relevancy score,
      sorted by the relevancy score in descending order. This list includes both documents initially marked as used
      and those specified as needed by the query state, ensuring that documents required for all sections are
      prioritized and included in the result.

    Note:
    - If the 'all_sections_needed' key does not exist in the query state or if it's marked as False, the method
      will simply return the `used_articles` list without any modifications.
    """
    if not query_state.used_articles_with_scores:
        return sorted(used_articles, key=lambda x: x[1], reverse=True)

    filenames = set([x[0] for x in query_state.used_articles_with_scores])
    missing_articles = [x for x in used_articles if x[0] not in filenames]
    total_articles = missing_articles + query_state.used_articles_with_scores
    total_articles = remove_duplicates(total_articles)
    # sort by relevancy for Mahesh
    return sorted(total_articles, key=lambda x: x[1], reverse=True)
