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

"""All backend config variables.

Update as needed to match your enivornment
"""
# GCP
PROJECT = '<YOUR GCP PROJECT ID>'
LOCATION = '<YOUR GCP PROJECT LOCATION>' # e.g. 'us-central1'

# Vertex Vector Search
ENDPOINT_ID = '<YOUR VERTEX VECTOR SEARCH ENDPOINT ID>' # e.g. '1641918305943945216'
DEPLOYED_INDEX = '<YOUR VERTEX VECTOR SEARCH DEPLOYED INDEX ID>' # e.g. 'flipkart_1702030773989'
NUM_NEIGHBORS = 7
FILTER_CATEGORIES = [ # List of category filter names from root to leaf
    'L0',
    'L1',
    'L2',
    'L3'
]

# BigQuery
PRODUCT_REFERENCE_TABLE = '<YOUR BQ TABLE NAME>' # e.g. 'project_name.flipkart.products'
COLUMN_ID = 'id'
COLUMN_CATEGORIES = [ # List of category column names from root to leaf
    'c0_name',
    'c1_name',
    'c2_name',
    'c3_name'
]
COLUMN_ATTRIBUTES = 'attributes'
COLUMN_DESCRIPTION = 'description'
ALLOW_TRAILING_NULLS = True # whether to allow trailing category levels to be 
                            # unspecified e.g (only top-level category is specified)

# Category
CATEGORY_DEPTH = len(COLUMN_CATEGORIES) # number of levels in category hierarchy to consider

# Testing - Update these for unit tests to run properly
TEST_GCS_IMAGE = 'gs://genai-product-catalog/toy_images/shorts.jpg' # Any image you have access to in GCS
TEST_PRODUCT_ID = '8f87b1af1e8ab42c1d559f2f9caf70bb' # Any valid product ID in reference table
TEST_CATEGORY_L0 = 'Clothing' # Any valid top level category. Case sensitive