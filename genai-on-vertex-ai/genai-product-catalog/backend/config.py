"""All backend config variables.

Update as needed to match your enivornment
"""
# GCP
PROJECT = 'solutions-2023-mar-107'
LOCATION = 'us-central1'

# Vertex Vector Search
ENDPOINT_ID = '8767655253467201536'
DEPLOYED_INDEX = 'muiltimodal_13K_train'
NUM_NEIGHBORS = 7

# BigQuery
PRODUCT_REFERENCE_TABLE = 'solutions-2023-mar-107.mercari.13K_synthetic_attributes_embeddings'
COLUMN_ID = 'id'
COLUMN_CATEGORIES = [ # List of category column names from root to leaf
    'c0_name',
    'c1_name',
    'c2_name',
]

# Category
CATEGORY_DEPTH = len(COLUMN_CATEGORIES) # number of levels in category hierarchy to consider

# Testing
GCS_TEST_IMAGE = 'gs://genai-product-catalog/toy_images/shorts.jpg' # Any image you have access to in GCS