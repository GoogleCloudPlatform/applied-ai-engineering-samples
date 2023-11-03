"""Expose REST API for product cataloging functionality."""
import os
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

import category

class Product(BaseModel):
    description: str
    main_image_base64: Optional[str] = None

app = FastAPI()

@app.post("/v1/categories/")
def suggest_categories(product: Product):
    return category.retrieve_and_rank(
        product.description, product.main_image_base64, base64=True)