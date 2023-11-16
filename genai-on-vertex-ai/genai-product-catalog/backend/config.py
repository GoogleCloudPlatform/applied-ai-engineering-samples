"""All backend config variables.

Update as needed to match your enivornment
"""
# GCP
PROJECT = 'solutions-2023-mar-107'
LOCATION = 'us-central1'

# Vertex Vector Search
ENDPOINT_ID = '5145507709805658112'
DEPLOYED_INDEX = 'flipkart_muiltimodal_18K'
NUM_NEIGHBORS = 7

# BigQuery
PRODUCT_REFERENCE_TABLE = 'solutions-2023-mar-107.flipkart.18K_no_duplicate_with_attributes'
COLUMN_ID = 'uniq_id'
COLUMN_CATEGORIES = [ # List of category column names from root to leaf
    'c0_name',
    'c1_name',
    'c2_name',
    'c3_name'
]
COLUMN_ATTRIBUTES = 'attributes'
ALLOW_TRAILING_NULLS = True # whether to allow trailing category levels to be 
                            # unspecified e.g (only top-level category is specified)

# Category
CATEGORY_DEPTH = len(COLUMN_CATEGORIES) # number of levels in category hierarchy to consider

# Attributes
ATTRIBUTES_FORMAT =  'key_value' # can be 'flat' or 'key_value'

# Testing
TEST_GCS_IMAGE = 'gs://genai-product-catalog/toy_images/shorts.jpg' # Any image you have access to in GCS
TEST_PRODUCT_ID = '8f87b1af1e8ab42c1d559f2f9caf70bb' # Any valid product ID in reference table