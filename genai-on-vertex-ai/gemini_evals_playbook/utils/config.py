import os
import sys
import configparser


def is_root_dir():
    """
    Checks if the current working directory is the root directory of a project 
    by looking for either the "/notebooks" or "/agents" folders.

    Returns:
        bool: True if either directory exists in the current directory, False otherwise.
    """

    current_dir = os.getcwd()
    # print("current dir: ", current_dir)
    notebooks_path = os.path.join(current_dir, "notebooks")
    agents_path = os.path.join(current_dir, "agents")
    
    return os.path.exists(notebooks_path) or os.path.exists(agents_path)

def read_config():
    if is_root_dir():
        current_dir = os.getcwd()
        config.read(current_dir + '/config.ini')
        root_dir = current_dir
    else:
        root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
        config.read(root_dir+'/config.ini')

    if not 'root_dir' in locals():  # If not found in any parent dir
        raise FileNotFoundError("config.ini not found in current or parent directories.")


def save_config(PROJECT_ID,
    LOCATION,
    STAGING_BUCKET,
    STAGING_BUCKET_URI,
    BQ_DATASET_ID,
    BQ_LOCATION,
    BQ_TABLES_SQL_PATH,
    BQ_PREFIX,
    BQ_T_EVAL_TASKS,
    BQ_T_EXPERIMENTS,
    BQ_T_PROMPTS,
    BQ_T_DATASETS,
    BQ_T_EVAL_RUN_DETAILS,
    BQ_T_EVAL_RUNS): 
    
    config = configparser.ConfigParser()

    if is_root_dir():
        current_dir = os.getcwd()
        config.read(current_dir + '/config.ini')
        root_dir = current_dir
    else:
        root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
        config.read(root_dir+'/config.ini')

    if not 'root_dir' in locals():  # If not found in any parent dir
        raise FileNotFoundError("config.ini not found in current or parent directories.")


    config['GCP']['PROJECT_ID'] = PROJECT_ID
    config['GCP']['LOCATION'] = LOCATION
    config['CLOUDSTORAGE']['STAGING_BUCKET'] = STAGING_BUCKET
    config['CLOUDSTORAGE']['STAGING_BUCKET_URI'] = STAGING_BUCKET_URI
    config['BIGQUERY']['BQ_DATASET_ID'] = BQ_DATASET_ID 
    config['BIGQUERY']['BQ_LOCATION'] = BQ_LOCATION
    config['BIGQUERY']['BQ_TABLES_SQL_PATH'] = BQ_TABLES_SQL_PATH
    config['BIGQUERY']['BQ_PREFIX'] = BQ_PREFIX
    config['BIGQUERY']['BQ_T_EVAL_TASKS'] = BQ_T_EVAL_TASKS
    config['BIGQUERY']['BQ_T_EXPERIMENTS'] = BQ_T_EXPERIMENTS
    config['BIGQUERY']['BQ_T_PROMPTS'] = BQ_T_PROMPTS
    config['BIGQUERY']['BQ_T_DATASETS'] = BQ_T_DATASETS
    config['BIGQUERY']['BQ_T_EVAL_RUN_DETAILS'] = BQ_T_EVAL_RUN_DETAILS
    config['BIGQUERY']['BQ_T_EVAL_RUNS'] = BQ_T_EVAL_RUNS

    with open(root_dir+'/config.ini', 'w') as configfile:  
        config.write(configfile)

    print('All configuration paramaters saved to file!')

def load_config():

    config = configparser.ConfigParser()

    if is_root_dir():
        current_dir = os.getcwd()
        config.read(current_dir + '/config.ini')
        root_dir = current_dir
    else:
        root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
        config.read(root_dir+'/config.ini')

    if not 'root_dir' in locals():  # If not found in any parent dir
        raise FileNotFoundError("config.ini not found in current or parent directories.")
        
    # Make variables global for modification
    global PROJECT_ID,LOCATION,STAGING_BUCKET,STAGING_BUCKET_URI,BQ_DATASET_ID,BQ_LOCATION,BQ_TABLES_SQL_PATH,BQ_PREFIX,BQ_T_EVAL_TASKS,BQ_T_EXPERIMENTS,BQ_T_PROMPTS,BQ_T_DATASETS,BQ_T_EVAL_RUN_DETAILS,BQ_T_EVAL_RUNS

    
    PROJECT_ID = config['GCP']['PROJECT_ID']
    LOCATION = config['GCP']['LOCATION']
    STAGING_BUCKET = config['CLOUDSTORAGE']['STAGING_BUCKET']
    STAGING_BUCKET_URI = config['CLOUDSTORAGE']['STAGING_BUCKET_URI']
    BQ_DATASET_ID = config['BIGQUERY']['BQ_DATASET_ID']
    BQ_LOCATION = config['BIGQUERY']['BQ_LOCATION']
    BQ_TABLES_SQL_PATH = config['BIGQUERY']['BQ_TABLES_SQL_PATH']
    BQ_PREFIX = config['BIGQUERY']['BQ_PREFIX']
    BQ_T_EVAL_TASKS = config['BIGQUERY']['BQ_T_EVAL_TASKS']
    BQ_T_EXPERIMENTS = config['BIGQUERY']['BQ_T_EXPERIMENTS']
    BQ_T_PROMPTS = config['BIGQUERY']['BQ_T_PROMPTS']
    BQ_T_DATASETS = config['BIGQUERY']['BQ_T_DATASETS']
    BQ_T_EVAL_RUN_DETAILS = config['BIGQUERY']['BQ_T_EVAL_RUN_DETAILS']
    BQ_T_EVAL_RUNS = config['BIGQUERY']['BQ_T_EVAL_RUNS']

config_parameters = load_config()