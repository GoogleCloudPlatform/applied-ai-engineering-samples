"""Functions related to attribute generation."""
import json
import logging
from typing import Union, Optional

import config
import embeddings
import nearest_neighbors
import utils

bq_client = utils.get_bq_client()
llm = utils.get_llm()
parameters = {
    "max_output_tokens": 256,
    "temperature": 0.0,
}

def join_attributes(
    ids: list[str]) -> dict[str:dict[str,str]]:
    """Gets the attributes for given product IDs.

    Args:
        ids: The product IDs to get the attributes for.

    Returns
        dict mapping product IDs to attributes. The attributes will themselves
         be a dict e.g.  {'color':'green', 'pattern': striped}
    """
    query = f"""
    SELECT
        {config.COLUMN_ID},
        {config.COLUMN_ATTRIBUTES}
    FROM
        `{config.PRODUCT_REFERENCE_TABLE}`
    WHERE
        {config.COLUMN_ID} IN {str(ids).replace('[','(').replace(']',')')}
    """
    query_job = bq_client.query(query)
    rows = query_job.result()
    attributes = {}
    for row in rows:
        attributes[row[config.COLUMN_ID]] = json.loads(row[config.COLUMN_ATTRIBUTES])
    return attributes

def retrieve(
    desc: str, 
    category: Optional[str] = None,
    image: Optional[str] = None, 
    base64: bool = False,
    num_neighbors: int = config.NUM_NEIGHBORS) -> list[dict]:
    """Returns list of attributes based on nearest neighbors.

    Embeds the provided desc and (optionally) image and returns the attributes
    corresponding to the closest products in embedding space. 
    
    TODO: If category is provided the retrieval is restricted to products in
     the same category.

    Args:
        desc: user provided description of product
        category: category of the product
        image: can be local file path, GCS URI or base64 encoded image
        base64: True indicates image is base64. False (default) will be 
          interpreted as image path (either local or GCS)
        num_neigbhors: number of nearest neighbors to return for EACH embedding

    Returns:
        List of candidates sorted by embedding distance. Each candidate is a
        dict with the following keys:
            id: product ID
            attributes: attributes in dict form e.g. {'color':'green', 'pattern': 'striped'}
            distance: embedding distance in range [0,1], 0 being the closest match
    """
    res = embeddings.embed(desc,image, base64)
    embeds = [res.text_embedding, res.image_embedding] if res.image_embedding else [res.text_embedding]
    neighbors = nearest_neighbors.get_nn(embeds)
    ids = [n.id[:-2] for n in neighbors] # last 3 chars are not part of product ID
    attributes = join_attributes(ids)
    candidates = [{'attributes':attributes[n.id[:-2]],'id':n.id, 'distance':n.distance}
                    for n in neighbors]
    return sorted(candidates, key=lambda d: d['distance'])

def generate_attributes(
    desc: str,
    category: Optional[str] = None,
    image: Optional[str] = None,
    base64: bool = False,
    num_neighbors: int = config.NUM_NEIGHBORS
) -> dict[str,str]:
    """Temporary Implementation

    Just returns attributes of nearest neighbor
    """
    candidates = retrieve(desc, category, image, base64, num_neighbors)
    return candidates[0]['attributes']