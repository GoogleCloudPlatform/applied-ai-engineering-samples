# Copyright 2023 Google LLC
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
# Author: Lei Pan

from __future__ import annotations
import vertexai
from vertexai.language_models import CodeGenerationModel

from google.cloud import discoveryengine_v1beta
from google.cloud.discoveryengine_v1beta.services.search_service import pagers
from google.protobuf.json_format import MessageToDict
import json
import time
from langchain.agents import AgentType, initialize_agent, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.chains.base import Chain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain
from langchain.llms import VertexAI
from langchain.llms.utils import enforce_stop_tokens
from langchain.prompts import StringPromptTemplate
from langchain.retrievers import GoogleCloudEnterpriseSearchRetriever as EnterpriseSearchRetriever
from langchain.schema import AgentAction, AgentFinish, Document, BaseRetriever
from langchain.tools import Tool
from langchain.utils import get_from_dict_or_env
from pydantic import BaseModel, Extra, Field, root_validator
import re
from typing import Any, Mapping, List, Dict, Optional, Tuple, Sequence, Union
import unicodedata
import vertexai
from vertexai.preview.language_models import TextGenerationModel
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.document_loaders import GCSDirectoryLoader
from langchain.embeddings import VertexAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from matching_engine import MatchingEngine
from matching_engine_utils import MatchingEngineUtils
from langchain.chains.router import MultiRetrievalQAChain
from langchain.chains import ConversationChain

VERTEX_API_PROJECT = 'your project id for vertex project'
VERTEX_API_LOCATION = 'location'

vertexai.init(project=VERTEX_API_PROJECT, location=VERTEX_API_LOCATION)


PROJECT_ID = "your project id for search engine project"
DOC_SEARCH_ENGINE_ID = "doc search engine id"
JIRA_SEARCH_ENGINE_ID = "jira search engine id"

# Utility functions for Embeddings API with rate limiting
def rate_limit(max_per_minute):
    period = 60 / max_per_minute
    print("Waiting")
    while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            print(".", end="")
            time.sleep(sleep_time)


class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):
    requests_per_minute: int
    num_instances_per_batch: int

    # Overriding embed_documents method
    def embed_documents(self, texts: List[str]):
        limiter = rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )
            chunk = self.client.get_embeddings(head)
            results.extend(chunk)
            next(limiter)

        return [r.values for r in results]
    

def get_rag_response(query):
    llm = VertexAI(model_name="text-unicorn@001", max_output_tokens=1024, temperature=0)

    EMBEDDING_QPM = 100
    EMBEDDING_NUM_BATCH = 5
    embeddings = CustomVertexAIEmbeddings(
    requests_per_minute=EMBEDDING_QPM,
    num_instances_per_batch=EMBEDDING_NUM_BATCH,
    )

    ME_REGION = "us-central1"
    ME_INDEX_NAME = f"{PROJECT_ID}-me-index"
    ME_EMBEDDING_DIR = f"{PROJECT_ID}-me-bucket"
    ME_DIMENSIONS = 768  # when using Vertex PaLM Embedding
    mengine = MatchingEngineUtils(PROJECT_ID, ME_REGION, ME_INDEX_NAME)
    ME_INDEX_ID, ME_INDEX_ENDPOINT_ID = mengine.get_index_and_endpoint()
    print(f"ME_INDEX_ID={ME_INDEX_ID}")
    print(f"ME_INDEX_ENDPOINT_ID={ME_INDEX_ENDPOINT_ID}")

    me = MatchingEngine.from_components(
    project_id=PROJECT_ID,
    region=ME_REGION,
    gcs_bucket_name=f"gs://{ME_EMBEDDING_DIR}".split("/")[2],
    embedding=embeddings,
    index_id=ME_INDEX_ID,
    endpoint_id=ME_INDEX_ENDPOINT_ID,
    )

    # Create chain to answer questions
    NUMBER_OF_RESULTS = 3
    SEARCH_DISTANCE_THRESHOLD = 0.6

    # Expose index to the retriever
    code_retriever = me.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": NUMBER_OF_RESULTS,
        "search_distance": SEARCH_DISTANCE_THRESHOLD,
    },
    )

    doc_retriever=EnterpriseSearchRetriever(
    project_id=PROJECT_ID,
    search_engine_id=DOC_SEARCH_ENGINE_ID,
    max_documents=3,
    )


    jira_retriever=EnterpriseSearchRetriever(
    project_id=PROJECT_ID,
    search_engine_id=JIRA_SEARCH_ENGINE_ID,
    max_documents=3,
    )

    retriever_infos = [
    {
        "name": "codebase search",
        "description": "Good for answering questions about the code in the codebase",
        "retriever": code_retriever
    },
    {
        "name": "coding style guide",
        "description": "Good for answering questions about coding styles such as python coding styles, java coding styles, c++ coding styles, etc",
        "retriever": doc_retriever
    },
    {
        "name": "jira issues search",
        "description": "Good for answering questions about jira issues",
        "retriever": jira_retriever
    }
    ]
    DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

    Current conversation:
    {history}
    Human: {input}
    AI:"""

    prompt_default_template = DEFAULT_TEMPLATE.replace('input', 'query')

    prompt_default = PromptTemplate(
        template=prompt_default_template, input_variables=['history', 'query']
    )
    default_chain=ConversationChain(llm=llm, prompt=prompt_default, input_key='query', output_key='result')

    chain = MultiRetrievalQAChain.from_retrievers(llm, retriever_infos, default_chain=default_chain)
    result = chain(query)['result']
    print(result)
    return result

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.

    Sample request:
    {
        "detectIntentResponseId":"e9d0482d-ae09-4152-9810-8b95c0b4286c",
        "intentInfo":{
            "lastMatchedIntent":"projects/dialogflow-cx-first-run/locations/global/agents/9a61d69a-007b-4af8-bc82-1eb0643361c3/intents/626965d9-6bb3-4724-88f3-cfdfef2315d0"
        },
        "pageInfo":{
            "currentPage":"projects/dialogflow-cx-first-run/locations/global/agents/9a61d69a-007b-4af8-bc82-1eb0643361c3/flows/00000000-0000-0000-0000-000000000000/pages/START_PAGE"
        },
        "sessionInfo":{
            "session":"projects/dialogflow-cx-first-run/locations/global/agents/9a61d69a-007b-4af8-bc82-1eb0643361c3/sessions/0ceccc-42b-72a-023-3c781b146",
            "parameters":{
                "foo":"bar"
            }
        },
        "fulfillmentInfo":{
            "tag":"hello-world"
        }
    }

    """
    request_json = request.get_json()
    print(request_json)

    prompt = ""
    if request_json.get('text', None):
        prompt = request_json['text']

    if request_json.get('fulfillmentInfo', None):
        tag = request_json['fulfillmentInfo']['tag']
        print('Tag: {}'.format(tag))
    elif request_json.get('queryResult', None):
        tag = 'dialogflow-es'
        print('Dialogflow ES webhook request')
    else:
        return ('Unrecognized request', 404)

    if tag == 'get-rag':
        # call rag and get a response:

        result = get_rag_response(prompt)
        # Set a response
        #result = "haha"
        print(f"debug result:{result}")
        response = {}
        response['fulfillmentResponse'] = {
            'messages': [
                {'text': {
                    'text': ['',
                             '']
                }
                },
                {'payload': {
                    'message_payload_1': 'Sample payload message1 ',
                    'message_payload_2': 'Sample payload message2'
                }
                }
            ]
        }

        # Update session variables
        response['sessionInfo'] = {
            'parameters': {
                'foo': result
            }
        }

        # Update custom payload
        response['payload'] = {
            'payload_1': 'Sample payload bla1',
            'payload_2': 'Sample payload bla2'
        }
        return response

    elif tag == 'dialogflow-es':
        # Set a response
        response = {}
        # response['fulfillmentText'] = ('This is fulfillment_text from the webhook')
        response['fulfillmentMessages'] = [
            {'text': {
                'text': ['This is response 1 from the webhook',
                         'This is response 2 from the webhook']
            }
            }
        ]
        return response

    else:
        return ('Not found', 404)