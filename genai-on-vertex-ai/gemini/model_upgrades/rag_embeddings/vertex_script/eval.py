# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import pandas as pd
import vertexai
from datetime import datetime
from vertexai.evaluation import EvalTask, PointwiseMetric


def load_dataset(dataset_local_path: str):
    with open(dataset_local_path, 'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    df = pd.DataFrame(data)
    return df

def run_eval(experiment_name: str, model: str, embedding_model: str, prompt_template_local_path: str, dataset_local_path: str, metric_name: str):
  timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()

  with open(prompt_template_local_path, 'r') as f:
    prompt_template = f.read()
 
  metrics = EvalTask(
      dataset=load_dataset(dataset_local_path),
      metrics=[PointwiseMetric(
               metric=metric_name,
               metric_prompt_template= prompt_template
               )   
               ],
      experiment=experiment_name
  ).evaluate(
      response_column_name= 'retrieved_context',
      experiment_run_name=f"{timestamp}-{embedding_model}-{model.replace('.', '-')}"
  )

  return f"Average score for {embedding_model} model retrieval quality:", round(metrics.summary_metrics[f'{metric_name}/mean'],3)



if __name__ == '__main__':
    if os.getenv("PROJECT_ID", "your-project-id") == "your-project-id":
        raise ValueError("Please configure your Google Cloud Project ID.")
    vertexai.init(project=os.getenv("PROJECT_ID"), location='us-central1')
    
    baseline_run=run_eval(
        experiment_name = 'evals-ragembeddings-demo',
        model = 'gemini-2.0-flash',
        embedding_model= 'text-embedding-004',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'baseline_dataset.jsonl',
        metric_name = 'retrieval_quality'
    )

    candidate_run=run_eval(
        experiment_name = 'evals-ragembeddings-demo',
        model = 'gemini-2.0-flash',
        embedding_model= 'text-embedding-005',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'candidate_dataset.jsonl',
        metric_name = 'retrieval_quality'
    )
    print(baseline_run)
    print(candidate_run)
