"""Functions for Vertex Vector Search."""
from collections import namedtuple
from google.cloud import aiplatform
import config

Neighbor = namedtuple('Neighbor',['id', 'distance'])
index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=config.ENDPOINT_ID,
    project=config.PROJECT,
    location=config.LOCATION
)

def get_nn(embeds: list[list[float]], num_neighbors: int = config.NUM_NEIGHBORS) -> list[Neighbor]:
    """Fetch nearest neigbhors in vector store.

    Neighbors are fetched independently for each embedding then unioned.

    Args:
        embeds: list of embeddings to find neareast neighbors
        num_neigbhors: number of nearest neighbors to return EACH embedding

    Returns:
        A list of named tuples containing the the following attributes
            id: unique item identifier, usually used to join to a reference DB
            distance: the embedding distance
    """
    response = index_endpoint.find_neighbors(
        deployed_index_id=config.DEPLOYED_INDEX,
        queries=embeds,
        num_neighbors=num_neighbors,
    )
    return [Neighbor(r.id, r.distance) for neighbor in response for r in neighbor]
