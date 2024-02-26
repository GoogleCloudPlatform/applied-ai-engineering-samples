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

from typing import List

from google.cloud import discoveryengine_v1beta as discoveryengine


def search_followup(
    conversation_client: discoveryengine.ConversationalSearchServiceClient,
    conversation_name: str,
    query: str,
    project_id: str,
    datastore_location: str,
    datastore_id: str,
    serving_config_id: str = "default_config",
    summary_result_count: int = 5,
    include_citations: bool = True,
) -> List[discoveryengine.ConverseConversationResponse]:
    request = discoveryengine.ConverseConversationRequest(
        name=conversation_name,
        query=discoveryengine.TextInput(input=query),
        serving_config=conversation_client.serving_config_path(
            project=project_id,
            location=datastore_location,
            data_store=datastore_id,
            serving_config=serving_config_id,
        ),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=summary_result_count,
            include_citations=include_citations,
        ),
    )

    response = conversation_client.converse_conversation(request)

    return response


def get_document_from_ids(
    document_client: discoveryengine.DocumentServiceClient,
    project_id: str,
    datastore_location: str,
    datastore_id: str,
    document_id: str,
    branch: str = "default_branch",
) -> List[discoveryengine.Document]:
    request = discoveryengine.GetDocumentRequest(
        name=document_client.document_path(
            project=project_id,
            location=datastore_location,
            data_store=datastore_id,
            branch=branch,
            document=document_id,
        )
    )

    response = document_client.get_document(request)

    return response


def recommend_items(
    recommendation_client: discoveryengine.RecommendationServiceClient,
    documents: str,
    project_id: str,
    datastore_location: str,
    datastore_id: str,
    serving_config_id: str = "default_config",
    user_pseudo_id: str = "xxxxxxx",
) -> List[discoveryengine.RecommendResponse.RecommendationResult]:
    user_event = discoveryengine.UserEvent()
    user_event.event_type = "view-item"
    user_event.user_pseudo_id = user_pseudo_id
    user_event.documents = [{"id": documents}]

    request = discoveryengine.RecommendRequest(
        serving_config=recommendation_client.serving_config_path(
            project=project_id,
            location=datastore_location,
            data_store=datastore_id,
            serving_config=serving_config_id,
        ),
        user_event=user_event,
    )

    response = recommendation_client.recommend(request)
    return response


def search_regular(
    search_client: discoveryengine.SearchServiceClient,
    search_query: str,
    project_id: str,
    datastore_location: str,
    datastore_id: str,
    serving_config_id: str = "default_config",
    return_snippet: bool = True,
    summary_result_count: int = 5,
    include_citations: bool = True,
) -> List[discoveryengine.SearchResponse.SearchResult]:
    serving_config = search_client.serving_config_path(
        project=project_id,
        location=datastore_location,
        data_store=datastore_id,
        serving_config=serving_config_id,
    )

    snippet_spec = discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=return_snippet
    )
    summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=summary_result_count, include_citations=include_citations
    )
    content_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=snippet_spec, summary_spec=summary_spec
    )

    # Create SearchRequest
    request = discoveryengine.SearchRequest(
        content_search_spec=content_spec,
        serving_config=serving_config,
        query=search_query,
        page_size=5,
    )

    response = search_client.search(request)
    return response
