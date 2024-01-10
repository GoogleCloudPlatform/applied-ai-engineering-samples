
### gcloud auth application-default login
from vertexai.preview.language_models import CodeGenerationModel
from vertexai.preview.language_models import CodeChatModel
from vertexai.preview.language_models import TextGenerationModel
from google.cloud import bigquery
import pandas_gbq 

# LOAD CONFIG DATA 
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
TABLE_ID = config['CREDENTIALS']['TABLE_ID']
PROJECT_ID = config['CREDENTIALS']['PROJECT_ID']


def bq_to_df(): 
    # Construct a BigQuery client object.

    sql = f"""
    SELECT *
    FROM `{TABLE_ID}`
    """
    df = pandas_gbq.read_gbq(sql, project_id=PROJECT_ID)

    return df
