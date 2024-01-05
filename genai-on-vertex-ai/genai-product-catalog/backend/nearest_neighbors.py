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

"""Functions for Vertex Vector Search."""
from collections import namedtuple
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace

import config
import logging

Neighbor = namedtuple('Neighbor',['id', 'distance'])
index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=config.ENDPOINT_ID,
    project=config.PROJECT,
    location=config.LOCATION
)

def get_nn(
    embeds: list[list[float]], 
    filters: list[str] = [], 
    num_neighbors: int = config.NUM_NEIGHBORS) -> list[Neighbor]:
    """Fetch nearest neigbhors in vector store.

    Neighbors are fetched independently for each embedding then unioned.

    Args:
        embeds: list of embeddings to find neareast neighbors
        filters: category prefix to restrict results to
        - example 1: ['Mens']
            will only return suggestiongs with top level category 'Mens'
        - example 2: ['Mens', 'Pants']
            will only return suggestions with top level category 'Mens'
            and second level category 'Pants'
        num_neigbhors: number of nearest neighbors to return for EACH embedding

    Returns:
        A list of named tuples containing the the following attributes
            id: unique item identifier, usually used to join to a reference DB
            distance: the embedding distance
    """
    if len(filters) > config.CATEGORY_DEPTH:
        logging.warning(f'''Number of category filters {len(filters)} is greater
         than supported category depth {config.CATEGORY_DEPTH}. Truncating''')
        filters = filters[:config.CATEGORY_DEPTH]

    filters = [Namespace(config.FILTER_CATEGORIES[i],[f]) for i,f in enumerate(filters)]
    response = index_endpoint.find_neighbors(
        deployed_index_id=config.DEPLOYED_INDEX,
        queries=embeds,
        num_neighbors=num_neighbors,
        filter=filters
    )
    return [Neighbor(r.id, r.distance) for neighbor in response for r in neighbor]
