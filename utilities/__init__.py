import configparser
import os
import sys
module_path = os.path.abspath(os.path.join('..'))

config = configparser.ConfigParser()

# Provide the file location depending on the starting point of the script
print("module path: ", module_path)
if 'talktodata' in module_path: 
    config.read(module_path+'/config.ini')
    root_dir = module_path

elif 'Talk2Data' in module_path: 
    config.read(module_path+'/config.ini')
    root_dir = module_path

else: 
    config.read('config.ini')
    root_dir = os.path.abspath(os.path.join(''))


#[CONFIG]
EMBEDDING_MODEL = config['CONFIG']['EMBEDDING_MODEL']
DATA_SOURCE = config['CONFIG']['DATA_SOURCE'] 
VECTOR_STORE = config['CONFIG']['VECTOR_STORE']

EXAMPLES = config.getboolean('CONFIG','EXAMPLES')
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
BQ_TALK2DATA_DATASET_NAME = config['BIGQUERY']['BQ_TALK2DATA_DATASET_NAME']
BQ_LOG_TABLE_NAME = config['BIGQUERY']['BQ_LOG_TABLE_NAME']
BQ_TABLE_LIST = config['BIGQUERY']['BQ_TABLE_LIST']



__all__ = ["EMBEDDING_MODEL",
           "DATA_SOURCE",
           "VECTOR_STORE",
           "CACHING",
           "EXAMPLES",
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
           "BQ_TALK2DATA_DATASET_NAME",
           "BQ_LOG_TABLE_NAME",
           "BQ_TABLE_LIST",
           "root_dir"]