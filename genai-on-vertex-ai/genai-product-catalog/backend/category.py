"""Functions related to product categorization"""
from typing import Optional
from google.cloud import aiplatform
from google.cloud import bigquery
import config
import embeddings
import nearest_neighbors

bq_client = bigquery.Client(config.PROJECT)

def join_categories(
    ids: list[str], 
    category_depth:int = config.CATEGORY_DEPTH) -> dict:
    """Given list of product IDs, join category names.
    
    Args:
        ids: list of product IDs used to join against master product table
        category_depth: number of levels in category hierarchy to return

    Returns:
        dict mapping product IDs to category name (id:category_name)
    """
    query = f"""
    SELECT
        {config.COLUMN_ID},
        {','.join(config.COLUMN_CATEGORIES[:category_depth])}
    FROM
        `{config.PRODUCT_REFERENCE_TABLE}`
    WHERE
        id IN {str(ids).replace('[','(').replace(']',')')}
    """
    query_job = bq_client.query(query)
    rows = query_job.result()
    categories = {} 
    for row in rows:
        categories[row['id']] = [row['c0_name'],row['c1_name'],row['c2_name']]
    return categories


def gen_candidates(
    desc: str, 
    image_uri: Optional[str] = None, 
    num_neighbors: int = config.NUM_NEIGHBORS):
    """Returns list of possible categories ranked by embedding distance.

    Args:
        desc: user provided description of product
        image_uri: GCS URI of product image
    """
    res = embeddings.embed(desc,image_uri)
    embeds = [res.text_embedding, res.image_embedding] if res.image_embedding else [res.text_embedding]
    neighbors = nearest_neighbors.get_nn(embeds)
    ids = [n.id[:-2] for n in neighbors] # last 3 chars are not part of product ID
    categories = join_categories(ids)
    candidates = [{'category':categories[n.id[:-2]],'id':n.id, 'distance':n.distance}
                    for n in neighbors]
    return sorted(candidates, key=lambda d: d['distance'])
