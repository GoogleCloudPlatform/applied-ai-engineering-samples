import json
import os
import pandas as pd
import vertexai
from datetime import datetime
from vertexai.evaluation import EvalTask, MetricPromptTemplateExamples
from vertexai.generative_models import GenerativeModel

def load_dataset(dataset_local_path: str):
    with open(dataset_local_path, 'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    df = pd.DataFrame(data)
    df['document_text'] = df['document_path'].apply(lambda doc_path: open(doc_path, 'r').read())
    return df[['document_text', 'reference']]

def run_eval(experiment_name: str, baseline_model: str, candidate_model: str, prompt_template_local_path: str, dataset_local_path: str):
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    prompt_template = open(prompt_template_local_path).read()
    task = EvalTask(
        dataset=load_dataset(dataset_local_path),
        metrics=[MetricPromptTemplateExamples.Pointwise.SUMMARIZATION_QUALITY],
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
    print(f"Baseline model score: {baseline_results.summary_metrics['summarization_quality/mean']:.2f}")
    print(f"Candidate model score: {candidate_results.summary_metrics['summarization_quality/mean']:.2f}")

if __name__ == '__main__':
    if os.getenv("PROJECT_ID", "your-project-id") == "your-project-id":
        raise ValueError("Please configure your Google Cloud Project ID.")
    vertexai.init(project=os.getenv("PROJECT_ID"), location='us-central1')
    run_eval(
        experiment_name = 'eval-summarization-demo',
        baseline_model = 'gemini-1.5-flash-002',
        candidate_model = 'gemini-2.0-flash-001',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'dataset.jsonl'    
    )