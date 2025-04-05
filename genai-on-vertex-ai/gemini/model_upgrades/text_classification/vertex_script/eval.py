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
import vertexai
from datetime import datetime
from vertexai.evaluation import EvalTask, CustomMetric
from vertexai.generative_models import GenerativeModel

def case_insensitive_match(record: dict[str, str]) -> dict[str, float]:
    response = record["response"].strip().lower()
    label = record["reference"].strip().lower()
    return {"accuracy": 1.0 if label == response else 0.0}

def run_eval(experiment_name: str, baseline_model: str, candidate_model: str, prompt_template_local_path: str, dataset_local_path: str):
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    prompt_template = open(prompt_template_local_path).read()
    task = EvalTask(
        dataset=dataset_local_path,
        metrics=[CustomMetric(name="accuracy", metric_function=case_insensitive_match)],
        experiment=experiment_name
    )
    baseline_results = task.evaluate(
        experiment_run_name=f"{timestamp}-{baseline_model.replace('.', '-')}",
        prompt_template=prompt_template,
        model=GenerativeModel(baseline_model)
    )
    candidate_results = task.evaluate(
        experiment_run_name=f"{timestamp}-{candidate_model.replace('.', '-')}",
        prompt_template=prompt_template,
        model=GenerativeModel(candidate_model)
    )
    print("Baseline model accuracy:", baseline_results.summary_metrics["accuracy/mean"])
    print("Candidate model accuracy:", candidate_results.summary_metrics["accuracy/mean"])

if __name__ == '__main__':
    if os.getenv("PROJECT_ID", "your-project-id") == "your-project-id":
        raise ValueError("Please configure your Google Cloud Project ID.")
    vertexai.init(project=os.getenv("PROJECT_ID"), location='us-central1')
    baseline=run_eval(
        experiment_name = 'evals-classifier-demo',
        baseline_model = 'gemini-1.0-pro-002',
        candidate_model = 'gemini-2.0-flash-001',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'dataset.jsonl'    
    )
