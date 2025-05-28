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
from vertexai.evaluation import EvalTask,PairwiseMetric, MetricPromptTemplateExamples
from vertexai.generative_models import GenerativeModel


def load_dataset(dataset_local_path: str):
    with open(dataset_local_path, 'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    df = pd.DataFrame(data)
    return df


def run_eval(experiment_name: str, baseline_model: str, candidate_model: str, prompt_template_local_path: str, dataset_local_path: str, metric_name: str):
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    prompt_template = open(prompt_template_local_path).read()
    metric = PairwiseMetric(
        metric=metric_name,
        metric_prompt_template=MetricPromptTemplateExamples.Pairwise.INSTRUCTION_FOLLOWING.metric_prompt_template,
        baseline_model=GenerativeModel(baseline_model),
    )
    task = EvalTask(
        dataset=load_dataset(dataset_local_path),
        metrics=[metric],
        experiment=experiment_name
    )
    results = task.evaluate(
        model=GenerativeModel(candidate_model),
        prompt_template=prompt_template,
        experiment_run_name=f"{timestamp}-{candidate_model.replace('.', '-')}"
    )    
    print("Baseline model win rate:", round(results.summary_metrics[f'{metric_name}/baseline_model_win_rate'],3))
    print("Candidate model win rate:", round(results.summary_metrics[f'{metric_name}/candidate_model_win_rate'],3))

if __name__ == '__main__':
    if os.getenv("PROJECT_ID", "your-project-id") == "your-project-id":
        raise ValueError("Please configure your Google Cloud Project ID.")
    vertexai.init(project=os.getenv("PROJECT_ID"), location='us-central1')
    
    baseline=run_eval(
        experiment_name = 'evals-instructionfollowing-demo',
        baseline_model = 'gemini-1.5-flash',
        candidate_model = 'gemini-2.0-flash',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'dataset.jsonl',
        metric_name = 'pairwise_instruction_following'
    )
    