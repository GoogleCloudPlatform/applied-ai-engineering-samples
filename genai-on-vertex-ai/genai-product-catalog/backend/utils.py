"""Functions common to several modules."""
from functools import cache
from google.cloud import bigquery
import vertexai
import config

@cache
def get_bq_client(project=config.PROJECT):
    return bigquery.Client(project)

@cache
def get_llm(project=config.PROJECT, location=config.LOCATION):
    vertexai.init(project=config.PROJECT, location=config.LOCATION)
    return vertexai.language_models.TextGenerationModel.from_pretrained("text-bison")


