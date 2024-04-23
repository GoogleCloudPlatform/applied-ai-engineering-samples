import configparser
import os
import sys

module_path = os.path.abspath(os.path.join('..'))
config = configparser.ConfigParser()

current_dir = os.getcwd()

# while current_dir != os.path.dirname(current_dir):  # Loop until root dir
#     if any(prefix in current_dir for prefix in module_prefixes):
#         config_path = os.path.join(current_dir, 'config.ini')
#         print(config_path)
#         if os.path.exists(config_path):
#             config.read(config_path)
#             root_dir = current_dir
#             break  # Stop searching once found
#     current_dir = os.path.dirname(current_dir)  # Move to parent dir

# print("module path: ", module_path)

module_prefixes = ["Talk2Data", "open-data-qna", "applied-ai-engineering-samples"]
if any(prefix in module_path for prefix in module_prefixes):
    config.read(module_path + '/config.ini')
    root_dir = module_path
else: 
    config.read('config.ini')
    root_dir = os.path.abspath(os.path.join(''))

if not 'root_dir' in locals():  # If not found in any parent dir
    raise FileNotFoundError("config.ini not found in current or parent directories.")

print(f'root_dir set to: {root_dir}')

# [CONFIG]
EMBEDDING_MODEL = config['CONFIG']['EMBEDDING_MODEL']
DATA_SOURCE = config['CONFIG']['DATA_SOURCE'] 
VECTOR_STORE = config['CONFIG']['VECTOR_STORE']

CACHING = config.getboolean('CONFIG','CACHING')
DEBUGGING = config.getboolean('CONFIG','DEBUGGING')
LOGGING = config.getboolean('CONFIG','LOGGING')

#[GCP]
PROJECT_ID =  config['GCP']['PROJECT_ID']

#[PGCLOUDSQL]
PG_REGION = config['PGCLOUDSQL']['PG_REGION']
PG_SCHEMA = config['PGCLOUDSQL']['PG_SCHEMA'] 
PG_INSTANCE = config['PGCLOUDSQL']['PG_INSTANCE']
PG_DATABASE = config['PGCLOUDSQL']['PG_DATABASE'] 
PG_USER = config['PGCLOUDSQL']['PG_USER'] 
PG_PASSWORD = config['PGCLOUDSQL']['PG_PASSWORD']

#[BIGQUERY]
BQ_REGION = config['BIGQUERY']['BQ_DATASET_REGION']
BQ_DATASET_NAME = config['BIGQUERY']['BQ_DATASET_NAME']
BQ_OPENDATAQNA_DATASET_NAME = config['BIGQUERY']['BQ_OPENDATAQNA_DATASET_NAME']
BQ_LOG_TABLE_NAME = config['BIGQUERY']['BQ_LOG_TABLE_NAME']
BQ_TABLE_LIST = config['BIGQUERY']['BQ_TABLE_LIST']



__all__ = ["EMBEDDING_MODEL",
           "DATA_SOURCE",
           "VECTOR_STORE",
           "CACHING",
           "DEBUGGING",
           "LOGGING",
           "PROJECT_ID",
           "PG_REGION",
           "PG_SCHEMA",
           "PG_INSTANCE",
           "PG_DATABASE",
           "PG_USER",
           "PG_PASSWORD", 
           "BQ_REGION",
           "BQ_DATASET_NAME",
           "BQ_OPENDATAQNA_DATASET_NAME",
           "BQ_LOG_TABLE_NAME",
           "BQ_TABLE_LIST",
           "root_dir"]