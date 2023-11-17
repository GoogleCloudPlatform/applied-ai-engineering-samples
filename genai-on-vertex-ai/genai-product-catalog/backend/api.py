"""Expose REST API for product cataloging functionality."""
import os
from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel

import attributes
import category
import marketing

class Product(BaseModel):
    description: str
    category: Optional[list[str]] = None
    main_image_base64: Optional[str] = None

app = FastAPI()

@app.post("/v1/categories/")
def suggest_categories(product: Product) -> list[list[str]]:
    """Suggest categories for product.
    
    Args:
    - description: Sparse description of product
    - category (optional): If one or more category levels is known
        include this to restrict the suggestions space. NOT YET IMPLEMENTED
        - example 1: ['Mens']
            will only return suggestiongs with top level category 'Mens'
        - example 2: ['Mens', 'Pants']
            will only return suggestions with top level category 'Mens'
            and second level category 'Pants'
    - main_image_base64 (optional): base64 encoded string representing product
            image.

    Returns:

    The category suggestions ordered from high to low confidence. Returned as
    a list of lists. Each inner list represents one fully qualified category
    with each string in the list representing a category level e.g. 
    ['Mens', 'Pants', 'Jeans']
    """
    return category.retrieve_and_rank(
        product.description, product.main_image_base64, base64=True)

@app.post("/v1/marketing/")
def generate_marketing_copy(
    description: str, attributes: dict[str, str]) -> str:
    """Generate Marketing Copy.
    
    Args:
    - description: sparse description of product
    - attributes: pass as JSON key value pairs e.g. {'color':'green', 'pattern': 'striped'}

    Returns:
    
    Marketing copy that can be used for a product page.
    """
    return marketing.generate_marketing_copy(description, attributes)

@app.post("/v1/attributes/")
def suggest_attributes(product: Product) -> dict[str,str]:
    """Suggests attributes for product.

    Args:
    - description: Sparse description of product
    - category (optional): If category is known this will be considered in
        generating relevant attributes. NOT YET IMPLEMENTED
    - main_image_base64 (optional): base64 encoded string representing product
            image.

    Returns:
    
    JSON dictionary representing attributes as key value pairs e.g. 
    {'color':'green', 'pattern': 'striped'}
    """
    return attributes.generate_attributes(
        product.description, product.category, product.main_image_base64, base64=True)