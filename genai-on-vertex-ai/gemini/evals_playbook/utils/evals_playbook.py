# Copyright 2024 Google LLC
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

import os
import itertools
import random
import string
import hashlib
import uuid
import json
import re
import datetime

import pandas as pd

from utils import config as cfg
from google.cloud import bigquery
from google.cloud import aiplatform
from google.cloud import storage
from vertexai.evaluation import EvalResult

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData, Column, String, Table
from utils.config import PROJECT_ID, LOCATION, STAGING_BUCKET


BQ_TABLE_MAP = {
    "tasks":        {"table_name": cfg.BQ_T_EVAL_TASKS, "keys": ["task_id"]},
    "experiments":  {"table_name": cfg.BQ_T_EXPERIMENTS, "keys": ["task_id", "experiment_id"]},
    "prompts":      {"table_name": cfg.BQ_T_PROMPTS, "keys": ["prompt_id"]},
    "datasets":     {"table_name": cfg.BQ_T_DATASETS, "keys": ["dataset_id"]},
    "runs":         {"table_name": cfg.BQ_T_EVAL_RUNS, "keys": ["task_id", "experiment_id", "run_id"]},
    "run_details":  {"table_name": cfg.BQ_T_EVAL_RUN_DETAILS, "keys": ["task_id", "experiment_id", "run_id", "dataset_row_id"]}
}

def get_table_name_keys(table_class):
    if table_class not in BQ_TABLE_MAP:
        raise ValueError(f"Invalid table class '{table_class}'. Supported {list(BQ_TABLE_MAP.keys())}")
    table = BQ_TABLE_MAP[table_class]
    return table["table_name"], table["keys"]

def get_db_object(table_class):
    table_name, update_keys = get_table_name_keys(table_class)
    update_key_cols = [Column(key, String, primary_key=True) for key in update_keys]
    return table_name, update_key_cols

def get_db_classes():
    # Define engine, metadata and session
    engine = create_engine(f'bigquery://{cfg.PROJECT_ID}')
    metadata = MetaData()
    # Auto populate metadata
    for table_class in BQ_TABLE_MAP:
        table_name, update_key_cols = get_db_object(table_class)
        Table(table_name, metadata, *update_key_cols, autoload_with=engine, schema=cfg.BQ_DATASET_ID)
    # create objects
    Base = automap_base(metadata=metadata)
    Base.prepare()
    return Base

def format_dt(dt: datetime.datetime):
    return dt.strftime("%m-%d-%Y_%H:%M:%S")

def clean_string(source_string):
    clean_spaces = re.sub(' ', '_', source_string)
    return re.sub('[^a-zA-Z0-9 _\n\.]', '', clean_spaces.lower())

def write_to_gcs(gcs_path, data):
    if not gcs_path.startswith("gs://"):
        raise Exception(f"Invalid Cloud Storage path {gcs_path}. Pass a valid path starting with gs://")

    # check if data is a file or a string
    UPLOAD_AS_FILE = False
    if os.path.exists(data):
        UPLOAD_AS_FILE = True

    bucket = gcs_path.split("/")[2]
    object = "/".join(gcs_path.split("/")[3:])
    
    # Initialize the Cloud Storage client
    storage_client = storage.Client()
    
    # Get the bucket object
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(object)
    if UPLOAD_AS_FILE:
        blob.upload_from_filename(data)
    else:
        blob.upload_from_string(data)
    return blob.self_link

def generate_uuid(text: str):
    """Generate a uuid based on text"""
    hex_string = hashlib.md5(text.encode('UTF-8')).hexdigest()
    random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return str(uuid.UUID(hex=hex_string)) + "-" + random_id


class Evals():
    def __init__(self):
        Base = get_db_classes()
        self.Task = Base.classes.eval_tasks
        self.Experiment = Base.classes.eval_experiments
        self.Prompt = Base.classes.eval_prompts
        self.EvalDataset = Base.classes.eval_datasets
        self.EvalRunDetail = Base.classes.eval_run_details
        self.EvalRun = Base.classes.eval_runs

    def log_task(self, task):
        try:
            if isinstance(task, self.Task):
                task = task.__dict__
                if "_sa_instance_state" in task: task.pop("_sa_instance_state") 
            if not isinstance(task, dict):
                raise Exception(f"Invalid task object. Expected: `dict`. Actual: {type(task)}")
            self._upsert("tasks", task)
        except Exception as e:
            print(f"Failed to log task due to following error.")
            raise e
        
    def log_prompt(self, prompt):
        try:
            if isinstance(prompt, self.Prompt):
                prompt = prompt.__dict__
                if "_sa_instance_state" in prompt: prompt.pop("_sa_instance_state") 
            if not isinstance(prompt, dict):
                raise Exception(f"Invalid task object. Expected: `dict`. Actual: {type(prompt)}")
            self._upsert("prompts", prompt)
        except Exception as e:
            print(f"Failed to log prompt due to following error.")
            raise e
        
    def _get_all(self, table_class, limit_offset=20, as_dict=False):
        client = bigquery.Client(project=cfg.PROJECT_ID)
        table_name = BQ_TABLE_MAP.get(table_class).get("table_name")
        table_id = f"{cfg.PROJECT_ID}.{cfg.BQ_DATASET_ID}.{table_name}"
        table = client.get_table(table_id)
        cols = [schema.name for schema in table.schema]
            
        sql = f"""
            SELECT {", ".join(cols)}
            FROM `{table_id}`
            ORDER BY create_datetime DESC
            LIMIT {limit_offset}
        """
        df = client.query_and_wait(sql).to_dataframe()
        if as_dict:
            return df.to_dict(orient='records')
        else:
            return df

    def get_all_tasks(self, limit_offset=20, as_dict=False):
        return self._get_all("tasks", limit_offset, as_dict)

    def get_all_experiments(self, limit_offset=20, as_dict=False):
        return self._get_all("experiments", limit_offset, as_dict)
    
    def get_all_prompts(self, limit_offset=20, as_dict=False):
        return self._get_all("prompts", limit_offset, as_dict)
    
    def get_all_eval_runs(self, limit_offset=20, as_dict=False):
        return self._get_all("runs", limit_offset, as_dict)
    
    def get_all_eval_run_details(self, limit_offset=20, as_dict=False):
        return self._get_all("run_details", limit_offset, as_dict)


    def _get_one(self, table_class, where_keys, limit_offset=1, as_dict=False):
        client = bigquery.Client(project=cfg.PROJECT_ID)
        table_name = BQ_TABLE_MAP.get(table_class).get("table_name")
        table_id = f"{cfg.PROJECT_ID}.{cfg.BQ_DATASET_ID}.{table_name}"
        table = client.get_table(table_id)
        cols = [schema.name for schema in table.schema]
        
        if where_keys:
            where_clause = "WHERE "
            where_clause += "AND ".join([f"{k} = '{v}'"for k,v in where_keys.items()])
        sql = f"""
            SELECT {", ".join(cols)}
            FROM `{table_id}`
            {where_clause}
            ORDER BY create_datetime DESC
            LIMIT {limit_offset}
        """
        df = client.query_and_wait(sql).to_dataframe()
        if as_dict:
            return df.to_dict(orient='records')
        else:
            return df

    def get_experiment(self, experiment_id, task_id: str="", as_dict=False):
        where_keys = {}
        if experiment_id:
            where_keys["experiment_id"] = experiment_id
            if task_id:
                where_keys["task_id"] = task_id
            return self._get_one("experiments", where_keys, as_dict=as_dict)
        else:
            raise Exception(f"Experiment ID is required.")
        
    def get_prompt(self, prompt_id, as_dict=False):
        where_keys = {}
        if prompt_id:
            where_keys["prompt_id"] = prompt_id
            return self._get_one("prompts", where_keys, as_dict=as_dict)
        else:
            raise Exception(f"Prompt ID is required.")

    def get_eval_runs(self, experiment_id, experiment_run_id: str="", task_id: str="", as_dict=False):
        where_keys = {}
        if not experiment_run_id:
            print("[INFO] experiment_run_id not passed. Showing last 5 runs (if available).")
            limit_offset = 5
        else:
            where_keys["run_id"] = experiment_run_id
            limit_offset = 1
        if experiment_id:
            where_keys["experiment_id"] = experiment_id
            if task_id:
                where_keys["task_id"] = task_id

            # get experiment
            exp_df = self.get_experiment(experiment_id=experiment_id)
            exp_df = exp_df[["experiment_id", "experiment_desc", "prompt_id", "model_endpoint", "model_name", "generation_config"]]
            model_config_df_exp = pd.json_normalize(exp_df['generation_config'])
            exp_df = pd.concat([exp_df.drop('generation_config', axis=1), model_config_df_exp], axis=1)
            # get metrics
            metrics_df = self._get_one("runs", where_keys, limit_offset=limit_offset, as_dict=False)
            metrics_df = metrics_df[['experiment_id', 'run_id',  'metrics', 'task_id', 'create_datetime', 'update_datetime', 'tags']]
            metrics_df = pd.merge(exp_df, metrics_df, on='experiment_id', how='left')
            metrics_df['metrics'] = metrics_df['metrics'].apply(eval)
            metrics_df_exp = pd.json_normalize(metrics_df['metrics'])
            metrics_df = pd.concat([metrics_df.drop('metrics', axis=1), metrics_df_exp], axis=1)
            if as_dict:
                return metrics_df.T.to_dict(orient='records')
            else:
                return metrics_df.T
        else:
            raise Exception(f"experiment_id is required.")

    def compare_eval_runs(self, experiment_run_ids, as_dict=False):
        if not experiment_run_ids:
            raise Exception(f"experiment_run_ids are required to compare runs")

        if isinstance(experiment_run_ids, str):
            experiment_run_ids = [experiment_run_ids]
        if isinstance(experiment_run_ids, list):
            experiment_run_ids = ", ".join([f"'{run}'" for run in experiment_run_ids])

        table_prefix = f"{cfg.PROJECT_ID}.{cfg.BQ_DATASET_ID}"
        client = bigquery.Client(project=cfg.PROJECT_ID)

        sql = f"""
        SELECT
            runs.task_id,
            runs.run_id,
            runs.experiment_id,
            exp.experiment_desc,
            exp.model_endpoint, 
            exp.model_name,
            exp.generation_config,
            prompt.prompt_template,
            prompt.system_instruction,
            runs.metrics,
            runs.create_datetime
        FROM 
            `{table_prefix}.{BQ_TABLE_MAP.get('runs').get('table_name')}` runs
        JOIN 
            `{table_prefix}.{BQ_TABLE_MAP.get('experiments').get('table_name')}` exp
        ON 
            runs.experiment_id = exp.experiment_id
        LEFT JOIN 
            `{table_prefix}.{BQ_TABLE_MAP.get('prompts').get('table_name')}` prompt
        ON 
            exp.prompt_id = prompt.prompt_id
        WHERE runs.run_id IN ({experiment_run_ids})
        ORDER BY runs.create_datetime DESC
        """
        
        df = client.query_and_wait(sql).to_dataframe()

        # format metrics
        df['metrics'] = df['metrics'].apply(eval)
        df['generation_config'] = df['generation_config'].apply(eval)

        # print(f'df:  {df.columns}')
        # print(f"generation_config:  {df['generation_config']}")
        df_metrics_exp = pd.json_normalize(df['metrics'])
        df_config_exp = pd.json_normalize(df['generation_config'])

        df = pd.concat([df.drop(['metrics', 'generation_config'], axis=1), df_metrics_exp, df_config_exp], axis=1)
        
        # print(f'df_config_exp:  {df_config_exp.columns}')
        # print(f'df_metrics_exp:  {df_metrics_exp.columns}')
        # print(f'df:  {df.columns}')


        if as_dict:
            return df.T.to_dict(orient='records')
        else:
            return df.T

    def grid_search(self, task_id, experiment_run_ids, opt_metrics, opt_params):
        """
        Performs grid search on the evaluation results and returns the best parameter combinations for each metric.

        Args:
            task_id: The specific task ID to filter the results.
            experiment_run_ids: List of experiment run IDs to include in the grid search.
            opt_metrics: List of metrics to optimize (e.g., ["ROUGE_1", "BLEU"]).
            opt_params: List of parameters to consider in the grid search (e.g., ["prompt_template", "temperature"]).

        Returns:
            A dictionary where keys are the optimization metrics and values are the corresponding best parameter combinations.
        """

        # Get 
        grid_df = (self.compare_eval_runs(experiment_run_ids)).T

        # Filter the grid_df based on the task_id
        filtered_df = grid_df[grid_df['task_id'] == task_id]

        # Initialize a dictionary to store the best parameter combinations for each metric
        best_params = {}

        for metric in opt_metrics:
            # Convert metric name to the corresponding column name in grid_df
            metric_mean_col = metric.lower().replace("_", "_") + "/mean" 
            metric_std_col = metric.lower().replace("_", "_") + "/std"

            # Find the row with the highest value for the given metric
            best_row = filtered_df.loc[filtered_df[metric_mean_col].idxmax()]

            # Extract the values of the optimization parameters and the std from the best row
            best_params[metric] = {
                "params": {param: best_row[param] for param in opt_params},
                "metric_mean": best_row[metric_mean_col],
                "metric_std": best_row[metric_std_col]
            }

        return best_params  

    def get_eval_run_detail(self, experiment_run_id, task_id: str="", limit_offset=100, as_dict=False):
        where_keys = {}
        if not experiment_run_id:
            raise Exception(f"experiment_run_id is required is to get run detail.")

        where_keys["run_id"] = experiment_run_id

        if task_id:
            where_keys["task_id"] = task_id
        details_df = self._get_one("run_details", where_keys, limit_offset=limit_offset, as_dict=False)
        if as_dict:
            return details_df.T.to_dict(orient='records')
        else:
            # print(f"[INFO] Showing top {limit_offset} rows. For viewing more # of rows, pass `limit_offset`.")
            return details_df


    def _upsert(self, table_class, rows, debug=False):
        """Inserts or updates rows in the specified BigQuery table.

        Args:
            table_name: The name of the table.
            rows: A list of dictionaries where each dictionary represents a row.
            update_keys: A list of keys to use for updating existing rows.
        """

        table_name, update_keys = get_table_name_keys(table_class)

        if isinstance(rows, dict):
            rows = [rows]

        # Validate that update keys are present in all rows
        all_keys = set().union(*(d.keys() for d in rows))
        for row in rows:
            for key in update_keys:
                if key not in row:
                    raise ValueError(f"Update key '{key}' not found in row: {row}")

        # Get BigQuery table schema
        table_id = f"{cfg.PROJECT_ID}.{cfg.BQ_DATASET_ID}.{table_name}"
        client = bigquery.Client(project=cfg.PROJECT_ID)
        table = client.get_table(table_id)
        schema = {schema.name:schema.field_type for schema in table.schema}

        # Construct the MERGE query dynamically
        merge_query = f"""
            MERGE INTO `{table_id}` AS target
            USING (
                SELECT * FROM UNNEST(@rows)
            ) AS source
            ON {" AND ".join(f"target.{key} = source.{key}" for key in update_keys)}
        """

        if update_keys:
            merge_query += f"""     WHEN MATCHED THEN
                UPDATE SET {", ".join(f"target.{key} = source.{key}" for key in all_keys if key not in update_keys + ['create_datetime'])}
        """

        merge_query += f"""     WHEN NOT MATCHED THEN
                INSERT({", ".join([key for key in all_keys])})
                VALUES({", ".join(f"source.{key}" for key in all_keys)})
        """

        # Convert rows to BigQuery format 
        rows_for_query = []
        for row in rows:
            row_for_query = []
            for key, val in row.items():
                field_type = schema.get(key)
                if field_type == "BOOLEAN":
                    field_type = "BOOL"
                if (val is not None):
                    if isinstance(val, datetime.datetime):
                        val = val.isoformat()
                    if isinstance(val, list):
                        row_for_query.append(bigquery.ArrayQueryParameter(key, field_type, val))
                    else:
                        row_for_query.append(bigquery.ScalarQueryParameter(key, field_type, val))
            rows_for_query.append(bigquery.StructQueryParameter("x", *row_for_query))  

        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ArrayQueryParameter("rows", "STRUCT", rows_for_query)]
        )

        # -- DEBUGGING --
        print("MERGE Query:")
        print(merge_query)
        print("\nRows:")
        print(rows_for_query)
        # -- END DEBUGGING --

        query_job = client.query(merge_query, job_config=job_config)
        query_job.result()  # Wait for the MERGE to complete
    
    def log_experiment(self,
                       task_id,
                       experiment_id,
                       prompt,
                       model,
                       metric_config,
                       experiment_desc="",
                       is_streaming=False,
                       tags=[],
                       metadata={}):
        # create experiment object
        experiment = self.Experiment(
            experiment_id=experiment_id,
            experiment_desc=experiment_desc,
            task_id=task_id,
            prompt_id = prompt.prompt_id,
            elapsed_time = 0
        )

        # add model information
        experiment.model_name = model._model_name.split("/")[-1]
        experiment.model_endpoint = aiplatform.constants.base.API_BASE_PATH
        experiment.is_streaming = is_streaming

        # add generation config
        if model._generation_config and isinstance(model._generation_config, dict):
            experiment.generation_config = json.dumps(model._generation_config)
        
        # add safety settings
        if model._safety_settings:
            if isinstance(model._safety_settings, dict):
                safety_settings_as_dict = {
                    category.name: threshold.name
                    for category, threshold in model._safety_settings.items()
                }
            elif isinstance(model._safety_settings, list):
                safety_settings_as_dict = {
                    s.to_dict().get("category", "HARM_CATEGORY_UNSPECIFIED"):s.to_dict().get("threshold") 
                    for s in model._safety_settings
                }
            else:
                safety_settings_as_dict = {}
            experiment.safety_settings = json.dumps(safety_settings_as_dict)
        
        # add metric config
        experiment.metric_config = str(metric_config)

        # additional fields
        experiment.create_datetime = datetime.datetime.now()
        experiment.update_datetime = datetime.datetime.now()
        experiment.tags = tags
        if isinstance(metadata, dict):
            experiment.metadata = json.dumps(metadata)

        try:
            if isinstance(experiment, self.Experiment):
                experiment = experiment.__dict__
                if "_sa_instance_state" in experiment: experiment.pop("_sa_instance_state") 
            if not isinstance(experiment, dict):
                raise Exception(f"Invalid task object. Expected: `dict`. Actual: {type(experiment)}")
            self._upsert("experiments", experiment)
        except Exception as e:
            print(f"Failed to log experiment due to following error.")
            raise e

        return experiment
       
    def save_prompt_template(self, task_id, experiment_id, prompt_id, prompt_template):
        # Construct the full file path in the bucket
        fmt_prompt_id = clean_string(prompt_id)
        prefix = f'{task_id}/prompts/{experiment_id}'
        gcs_file_path = f'gs://{STAGING_BUCKET}/{prefix}/template_{fmt_prompt_id}.txt'
        # write to GCS
        write_to_gcs(gcs_file_path, prompt_template)
        print(f"Prompt template saved to {gcs_file_path} successfully!")
        
    def save_prompt(self, text, run_path, blob_name):
        """
        Saves the given text to a Google Cloud Storage bucket and returns the blob's URI.
        Args:
            text: The text to be saved.
            bucket_name: The name of the GCS bucket.
            blob_name: The desired name for the blob (file) in the bucket.
        Returns:
            The URI of the created blob.
        """
        # Construct the full file path in the bucket
        gcs_file_path = f'gs://{STAGING_BUCKET}/{run_path}/{blob_name}.txt'
        blob_link = write_to_gcs(gcs_file_path, text)
        return blob_link

    def log_eval_run(self,
                     experiment_run_id: str,
                     experiment,
                     eval_result,
                     run_path,
                     tags=[],
                     metadata={}):
        # log run details
        if not isinstance(eval_result, EvalResult):
            raise Exception(f"Invalid eval_result object. Expected: `vertexai.evaluation.EvalResult` Actual: {type(eval_result)}")
        if isinstance(experiment, dict):
            experiment = self.Experiment(**experiment)
        if not isinstance(experiment, self.Experiment):
            raise Exception(f"Invalid experiment object. Expected: `Experiment` Actual: {type(experiment)}")
        
        # get run details from the Rapid Eval evaluation task
        detail_df = eval_result.metrics_table.to_dict(orient="records")
        summary_dict = eval_result.summary_metrics
        non_metric_keys = ['context', 'reference', 'instruction', 'dataset_row_id', 'completed_prompt', 'response']
        # report_df = eval_result.metrics_table
        print(f'detail_df.keys: {detail_df[0].keys()}')

        # prepare run details        
        run_details = []
        for row in detail_df:
            row.get("prompt")
            metrics = {k: row[k] for k in row if k not in non_metric_keys}
            run_detail = dict(
                run_id=experiment_run_id,
                experiment_id=experiment.experiment_id,
                task_id=experiment.task_id,
                dataset_row_id=row.get("dataset_row_id"),
                system_instruction=row.get("instruction"),
                input_prompt_gcs_uri=self.save_prompt(row.get("prompt"), run_path, row.get("dataset_row_id")), 
                output_text=row.get("response"),
                ground_truth=row.get("reference"),
                metrics=json.dumps(metrics),
                # additional fields
                latencies=[],
                create_datetime=datetime.datetime.now(),
                update_datetime=datetime.datetime.now(),
                tags=tags,
                metadata=json.dumps(metadata) if isinstance(metadata, dict) else None
                )
            run_details.append(run_detail)
        
        try:
            self._upsert("run_details", run_details)
        except Exception as e:
            print(f"Failed to log run details due to following error.")
            raise e

        # prepare run summary metrics
        run_summary = dict(
            run_id=experiment_run_id,
            experiment_id=experiment.experiment_id,
            task_id=experiment.task_id,
            # dataset_row_id = experiment.dataset_row_id, 
            metrics=json.dumps(summary_dict),
            # additional fields
            create_datetime=datetime.datetime.now(),
            update_datetime=datetime.datetime.now(),
            tags=tags,
            metadata=json.dumps(metadata) if isinstance(metadata, dict) else None
        )
        
        try:
            self._upsert("runs", run_summary)
        except Exception as e:
            print(f"Failed to log run summary due to following error.")
            raise e