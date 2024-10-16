import os
import pkg_resources
import requests
from typing import Optional

import sentencepiece
import vertexai
from google.cloud.aiplatform_v1 import HarmCategory
from vertexai.generative_models import GenerativeModel, HarmBlockThreshold

from .model import ModelProvider


class Google(ModelProvider):
    """
    A wrapper class for interacting with Google's Gemini API, providing methods to encode text, generate prompts,
    evaluate models, and create LangChain runnables for language model interactions.

    Attributes:
        model_name (str): The name of the Google model to use for evaluations and interactions.
        model: An instance of the Google Gemini client for API calls.
        tokenizer: A tokenizer instance for encoding and decoding text to and from token representations.
    """

    DEFAULT_MODEL_KWARGS: dict = dict(max_output_tokens=300,
                                      temperature=0)
    VOCAB_FILE_URL = "https://raw.githubusercontent.com/google/gemma_pytorch/33b652c465537c6158f9a472ea5700e5e770ad3f/tokenizer/tokenizer.model"

    def __init__(self,
                 project_id: str,
                 model_name: str = "gemini-1.5-pro",
                 model_kwargs: dict = DEFAULT_MODEL_KWARGS,
                 vocab_file_url: str = VOCAB_FILE_URL):
        """
        Initializes the Google model provider with a specific model.

        Args:
            project_id (str): ID of the google cloud platform project to use
            model_name (str): The name of the Google model to use. Defaults to 'gemini-1.5-pro'.
            model_kwargs (dict): Model configuration. Defaults to {max_tokens: 300, temperature: 0}.
            vocab_file_url (str): Sentencepiece model file that defines tokenization vocabulary. Deafults to gemma
                tokenizer https://github.com/google/gemma_pytorch/blob/main/tokenizer/tokenizer.model
        """

        self.model_name = model_name
        self.model_kwargs = model_kwargs
        vertexai.init(project=project_id, location="us-central1")
        self.model = GenerativeModel(self.model_name)

        local_vocab_file = 'tokenizer.model'
        if not os.path.exists(local_vocab_file):
            response = requests.get(vocab_file_url)  # Download Tokenizer Vocab File (4MB)
            response.raise_for_status()

            with open(local_vocab_file, 'wb') as f:
                for chunk in response.iter_content():
                    f.write(chunk)
        self.tokenizer = sentencepiece.SentencePieceProcessor(local_vocab_file)

        resource_path = pkg_resources.resource_filename('needlehaystack', 'providers/Gemini_prompt.txt')

        # Generate the prompt structure for the model
        # Replace the following file with the appropriate prompt structure
        with open(resource_path, 'r') as file:
            self.prompt_structure = file.read()

    async def evaluate_model(self, prompt: str) -> str:
        """
        Evaluates a given prompt using the Google model and retrieves the model's response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The content of the model's response to the prompt.
        """
        response = await self.model.generate_content_async(
            prompt,
            generation_config=self.model_kwargs,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        return response.text

    def generate_prompt(self, context: str, retrieval_question: str) -> str:
        """
        Generates a structured prompt for querying the model, based on a given context and retrieval question.

        Args:
            context (str): The context or background information relevant to the question.
            retrieval_question (str): The specific question to be answered by the model.

        Returns:
            str: The text prompt
        """
        return self.prompt_structure.format(
            retrieval_question=retrieval_question,
            context=context)

    def encode_text_to_tokens(self, text: str) -> list[int]:
        """
        Encodes a given text string to a sequence of tokens using the model's tokenizer.

        Args:
            text (str): The text to encode.

        Returns:
            list[int]: A list of token IDs representing the encoded text.
        """
        return self.tokenizer.encode(text)

    def decode_tokens(self, tokens: list[int], context_length: Optional[int] = None) -> str:
        """
        Decodes a sequence of tokens back into a text string using the model's tokenizer.

        Args:
            tokens (list[int]): The sequence of token IDs to decode.
            context_length (Optional[int], optional): An optional length specifying the number of tokens to decode. If not provided, decodes all tokens.

        Returns:
            str: The decoded text string.
        """
        return self.tokenizer.decode(tokens[:context_length])


