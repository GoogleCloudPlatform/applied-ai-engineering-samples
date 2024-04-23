# Common Imports
import time
import datetime
from datetime import datetime, timezone
import hashlib
import vertexai
import pandas
import pandas_gbq
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import json
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from logging import exception
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

from llmModels import returnModel 




source_type='BigQuery'


# @markdown Provide the below details to start using the notebook
PROJECT_ID='steveswalker-sandbox' # @param {type:"string"}
REGION = 'us-central1' # @param {type:"string"}
DATAPROJECT_ID='bigquery-public-data'  # This needs to be adjusted when using the bq public bigquery-public-data


# BQ Schema (DATASET) where tables live
schema='imdb' # @param {type:"string"}.  ### DDL extraction performed at this level, for the entire schema
USER_DATASET= DATAPROJECT_ID + '.' + schema

# Execution Parameters
SQL_VALIDATION='ALL'
INJECT_ONE_ERROR=False
EXECUTE_FINAL_SQL=True
SQL_MAX_FIX_RETRY=3
AUTO_ADD_KNOWNGOOD_SQL=True

# # Analytics Warehouse
# ENABLE_ANALYTICS=True
# DATASET_NAME='nl2sql'
# DATASET_LOCATION='US'
# LOG_TABLE_NAME='query_logs'
# FULL_LOG_TEXT=''


# Palm Models to use
MODEL='gemini-pro' # @param {type:"string"}
CHAT_MODEL='codechat-bison-32k' # @param {type:"string"}
embeddings_model='textembedding-gecko@002'


# PGVECTOR (Cloud SQL Postgres) Info.
database_password = "hr_tutorial"  # @param {type:"string"}
instance_name = "pg15-nl2sql-pgvector"  # @param {type:"string"}
database_name = "nl2sql-admin"  # @param {type:"string"}
database_user = "nl2sql-admin"  # @param {type:"string"}

# TODO: WHAT ARE THESE VALS ???????? 
num_table_matches = 5
num_column_matches = 20
similarity_threshold = 0.1
num_sql_matches=3


## TODO: Hierarchical Navigable Small World (HNSW) graphs are among the top-performing indexes for vector similarity search
m =  24 # @param {type:"integer"}
ef_construction = 100  # @param {type:"integer"}
operator =  "vector_cosine_ops"  # @param ["vector_cosine_ops", "vector_l2_ops", "vector_ip_ops"]





# Load the model 
vertexai.init(project=PROJECT_ID, location=REGION)
model=returnModel(MODEL)
chat_model=returnModel(CHAT_MODEL)





get_columns_sql=f'''
SELECT
    TABLE_CATALOG as project_id, TABLE_SCHEMA as owner , TABLE_NAME as table_name, COLUMN_NAME as column_name,
    DATA_TYPE as data_type, ROUNDING_MODE as rounding_mode, description
  FROM
    {USER_DATASET}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS
  ORDER BY
   project_id, owner, table_name, column_name ;
'''


get_fkeys_sql=f'''
SELECT T.CONSTRAINT_CATALOG, T.CONSTRAINT_SCHEMA, T.CONSTRAINT_NAME,
T.TABLE_CATALOG as project_id, T.TABLE_SCHEMA as owner, T.TABLE_NAME as table_name, T.CONSTRAINT_TYPE,
T.IS_DEFERRABLE, T.ENFORCED, K.COLUMN_NAME
FROM
{USER_DATASET}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS T
JOIN {USER_DATASET}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE K
ON K.CONSTRAINT_NAME=T.CONSTRAINT_NAME
WHERE
T.CONSTRAINT_TYPE="FOREIGN KEY"
ORDER BY
project_id, owner, table_name
'''

get_pkeys_sql=f'''
SELECT T.CONSTRAINT_CATALOG, T.CONSTRAINT_SCHEMA, T.CONSTRAINT_NAME,
T.TABLE_CATALOG as project_id, T.TABLE_SCHEMA as owner, T.TABLE_NAME as table_name, T.CONSTRAINT_TYPE,
T.IS_DEFERRABLE, T.ENFORCED, K.COLUMN_NAME
FROM
{USER_DATASET}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS T
JOIN {USER_DATASET}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE K
ON K.CONSTRAINT_NAME=T.CONSTRAINT_NAME
WHERE
T.CONSTRAINT_TYPE="PRIMARY KEY"
ORDER BY
project_id, owner, table_name
'''


get_table_comments_sql=f'''
select TABLE_CATALOG as project_id, TABLE_SCHEMA as owner , TABLE_NAME as table_name, OPTION_NAME, OPTION_TYPE, OPTION_VALUE as comments
FROM
{USER_DATASET}.INFORMATION_SCHEMA.TABLE_OPTIONS
WHERE
 OPTION_NAME = "description"
ORDER BY
project_id, owner, table_name
'''


# TODO: Change name 
def schema_generator(sql):
  df = pandas_gbq.read_gbq(sql, project_id=PROJECT_ID)
  return df


def add_table_comments(columns_df, pkeys_df, fkeys_df, table_comments_df):

  for index, row in table_comments_df.iterrows():
    if row['comments'] is None: ## or row['comments'] is not None:
        context_prompt = f"""
        Generate table comments for the table {row['project_id']}.{row['owner']}.{row['table_name']}

        Parameters:
        - column metadata: {columns_df.to_markdown(index = False)}
        - primary key metadata: {pkeys_df.to_markdown(index = False)}
        - foreign keys metadata: {fkeys_df.to_markdown(index = False)}
        - table metadata: {table_comments_df.to_markdown(index = False)}
      """
        #context_query = model.predict(context_prompt, max_output_tokens = 256, temperature= 0.2)
        context_query = model.generate_content(context_prompt, stream=False)
        print(clean_sql(str(context_query.candidates[0])))
        table_comments_df.at[index, 'comments'] = clean_sql(str(context_query.candidates[0]))

  return table_comments_df




def add_column_comments(columns_df, pkeys_df, fkeys_df, table_comments_df):
  for index, row in columns_df.iterrows():
        context_prompt = f"""
        Generate comments for the column {row['project_id']}.{row['owner']}.{row['table_name']}.{row['column_name']}


        Parameters:
        - column metadata: {columns_df.to_markdown(index = False)}
        - primary key metadata: {pkeys_df.to_markdown(index = False)}
        - foreign keys metadata: {fkeys_df.to_markdown(index = False)}
        - table metadata: {table_comments_df.to_markdown(index = False)}

      """
        #context_query = model.generate_content(context_prompt, stream=False)
        #columns_df.at[index, 'column_comments'] = clean_sql(str(context_query.candidates[0]))
        columns_df.at[index, 'column_comments'] = clean_sql("my comments")

  return columns_df




def get_column_sample(columns_df):
  sample_column_list=[]

  for index, row in columns_df.iterrows():
    get_column_sample_sql=f'''
        SELECT STRING_AGG(CAST(value AS STRING)) as sample_values
        FROM UNNEST((SELECT APPROX_TOP_COUNT({row["column_name"]}, 5) as osn
                     FROM `{row["project_id"]}.{row["owner"]}.{row["table_name"]}`
                ))
    '''
    column_samples_df=schema_generator(get_column_sample_sql)
    sample_column_list.append(column_samples_df['sample_values'].to_string(index=False))

  columns_df["sample_values"]=sample_column_list
  return columns_df



def clean_sql(result):
  result = result.replace("```sql", "").replace("```", "")
  return result





columns_df=schema_generator(get_columns_sql)
fkeys_df=schema_generator(get_fkeys_sql)
pkeys_df=schema_generator(get_pkeys_sql)
table_comments_df=schema_generator(get_table_comments_sql)