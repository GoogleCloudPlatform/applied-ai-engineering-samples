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
from vertexai.evaluation import EvalTask
from vertexai.generative_models import GenerativeModel


def load_dataset(dataset_local_path: str):
    with open(dataset_local_path, 'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    df = pd.DataFrame(data)
    df['document_text'] = df['document_path'].apply(lambda doc_path: open(doc_path, 'r').read())
    return df[['question', 'reference', 'document_text']]


def run_eval(experiment_name: str, baseline_model: str, candidate_model: str, prompt_template_local_path: str, dataset_local_path: str, metrics: list[str]):
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    prompt_template = open(prompt_template_local_path).read()
    task = EvalTask(
        dataset=load_dataset(dataset_local_path),
        metrics=metrics,
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
    print("Baseline model Rouge:", round(baseline_results.summary_metrics['rouge_l_sum/mean'],3))
    print("Canidadate model Rouge:", round(candidate_results.summary_metrics['rouge_l_sum/mean'],3))
    print("Baseline model Bleu:", round(baseline_results.summary_metrics['bleu/mean'],3))
    print("Candidate model Bleu:", round(candidate_results.summary_metrics['bleu/mean'],3))

if __name__ == '__main__':
    if os.getenv("PROJECT_ID", "your-project-id") == "your-project-id":
        raise ValueError("Please configure your Google Cloud Project ID.")
    vertexai.init(project=os.getenv("PROJECT_ID"), location='us-central1')

    metrics = [
    "rouge_l_sum",
    "bleu",
]
    
    baseline=run_eval(
        experiment_name = 'evals-rag-demo',
        baseline_model = 'gemini-1.0-pro-001',
        candidate_model = 'gemini-2.0-flash',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'dataset.jsonl',
        metrics = metrics    
    )
    