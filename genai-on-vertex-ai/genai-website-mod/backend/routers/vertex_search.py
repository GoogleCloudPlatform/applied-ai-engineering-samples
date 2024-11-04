# noqa: E501

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

import tomllib

from fastapi import APIRouter, HTTPException
from google.cloud import discoveryengine_v1beta as discoveryengine
from models.vertex_search_models import (
    VertexRecommendRequest,
    VertexRecommendResponse,
    VertexSearchFirstConvRequest,
    VertexSearchFirstConvResponse,
    VertexSearchFollowupRequest,
    VertexSearchFollowupResponse,
)
from proto import Message
from utils.vertex_search_utils import (
    get_document_from_ids,
    recommend_items,
    search_followup,
)

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

project_id = config["global"]["project_id"]
location = config["global"]["location"]
datastore_id = config["global"]["datastore_id"]
datastore_location = config["global"]["datastore_location"]
serving_config = config["global"]["serving_config"]

converse_client = discoveryengine.ConversationalSearchServiceClient()

recommendation_client = discoveryengine.RecommendationServiceClient()
recs_datastore_id = config["global"]["recs_datastore_id"]
recs_serving_config_id = config["global"]["recs_serving_config_id"]

document_client = discoveryengine.DocumentServiceClient()


def create_new_conversation():
    converse_request = discoveryengine.CreateConversationRequest(
        parent=(f"projects/{project_id}/locations/{datastore_location}/"
                f"collections/default_collection/dataStores/{datastore_id}"
        ),  # noqa: E501
        conversation=discoveryengine.Conversation(),
    )
    conversation = converse_client.create_conversation(request=converse_request)

    return conversation


router = APIRouter()


def get_message_pairs(response):
    message_pairs = []
    user_messages = []
    bot_messages = []

    for res in response.get("conversation").get("messages"):
        if "user_input" in res:
            user_messages.append(res.get("user_input").get("input"))
        else:
            bot_messages.append(res.get("reply").get("summary").get("summary_text"))

    for i in range(len(user_messages)):
        message_pairs.append({"user": user_messages[i], "bot": bot_messages[i]})

    return message_pairs


def overwrite_link(link):
    list_link = link.split("/")
    page = list_link[-1]
    list_page = page.split(".")
    page_id = list_page[0]

    if page_id in ["1", "2", "3", "4", "5", "6"]:
        new_page_id = "/blog/" + page_id
    else:
        new_page_id = "/" + page_id + "/"

    return new_page_id


def get_search_results(response):
    search_results = []
    for res in response.get("search_results"):
        link = res.get("document").get("derived_struct_data").get("link")
        overwritten_link = overwrite_link(link)
        snippet = (
            res.get("document")
            .get("derived_struct_data")
            .get("snippets")[0]
            .get("snippet")
        )
        search_results.append({"link": overwritten_link, "snippet": snippet})
    return search_results


@router.post(path="/api/first-conversational-search")
def trigger_first_search(
    data: VertexSearchFirstConvRequest,
) -> VertexSearchFirstConvResponse:
    try:
        parent = (
            f"projects/{project_id}/locations/{datastore_location}/collections/default_collection/dataStores/{datastore_id}",  # noqa: E501
        )
        print(parent)

        conversation = create_new_conversation()
        print(conversation)

        response = search_followup(
            conversation_client=converse_client,
            conversation_name=conversation.name,
            query=data.search_query,
            project_id=project_id,
            datastore_location=datastore_location,
            datastore_id=datastore_id,
            serving_config_id=serving_config,
        )
        print(response)

    except Exception as e:
        print(f"ERROR: Vertex Conversational Search error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    else:
        response_dict = Message.to_dict(response)
        message_pairs = get_message_pairs(response_dict)
        search_results = get_search_results(response_dict)

        return VertexSearchFollowupResponse(
            conversation_name=conversation.name,
            search_results=search_results,
            message_pairs=message_pairs,
        )


@router.post(path="/api/conversational-search")
def trigger_followup_search(
    data: VertexSearchFollowupRequest,
) -> VertexSearchFollowupResponse:
    try:
        response = search_followup(
            conversation_client=converse_client,
            conversation_name=data.conversation_name,
            query=data.search_query,
            project_id=project_id,
            datastore_location=datastore_location,
            datastore_id=datastore_id,
            serving_config_id=serving_config,
        )

    except Exception as e:
        print(f"ERROR: Vertex Conversational Search error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    else:
        response_dict = Message.to_dict(response)
        message_pairs = get_message_pairs(response_dict)
        search_results = get_search_results(response_dict)

        return VertexSearchFollowupResponse(
            conversation_name=data.conversation_name,
            search_results=search_results,
            message_pairs=message_pairs,
        )


def get_docs_from_ids(document_ids):
    document_urls = []
    for document_id in document_ids:
        try:
            response = get_document_from_ids(
                document_client=document_client,
                project_id=project_id,
                datastore_location=datastore_location,
                datastore_id=recs_datastore_id,
                document_id=document_id,
            )

        except Exception as e:
            print(f"ERROR: Vertex Documents Parsing error -> {e}")
            raise HTTPException(status_code=500, detail=str(e))

        else:
            response_dict = Message.to_dict(response)
            document_url = response_dict.get("content").get("uri")
            document_urls.append(document_url)

    return document_urls


@router.post(path="/api/vertex-recommend-items")
def vertex_recommend_items(data: VertexRecommendRequest) -> VertexRecommendResponse:
    try:
        response = recommend_items(
            recommendation_client=recommendation_client,
            documents=data.document_id,
            project_id=project_id,
            datastore_location=datastore_location,
            datastore_id=recs_datastore_id,
            serving_config_id=recs_serving_config_id,
        )

    except Exception as e:
        print(f"ERROR: Vertex Recommendations error -> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    else:
        response_dict = Message.to_dict(response)
        response_results = response_dict.get("results")

        document_ids = []
        for result in response_results:
            document_ids.append(result.get("id"))

        document_urls = get_docs_from_ids(document_ids)

        return VertexRecommendResponse(recommended_items=document_urls)
