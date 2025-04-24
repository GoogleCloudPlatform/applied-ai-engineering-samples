import json
import os
import pandas as pd
import vertexai
from datetime import datetime
from vertexai.evaluation import EvalTask, EvalResult, MetricPromptTemplateExamples
from vertexai.generative_models import GenerativeModel

def load_dataset(dataset_local_path: str):
    with open(dataset_local_path, 'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    df = pd.DataFrame(data)
    df['document_text'] = df['document_path'].apply(lambda doc_path: open(doc_path, 'r').read())
    return df[['question', 'reference', 'document_text']]

def run_eval(experiment_name: str, baseline_model: str, candidate_model: str, prompt_template_local_path: str, dataset_local_path: str):
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    prompt_template = open(prompt_template_local_path).read()
    task = EvalTask(
        dataset=load_dataset(dataset_local_path),
        metrics=[MetricPromptTemplateExamples.Pointwise.QUESTION_ANSWERING_QUALITY],
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
    print(f"Baseline model score: {baseline_results.summary_metrics['question_answering_quality/mean']*20:.1f}%")
    print(f"Candidate model score: {candidate_results.summary_metrics['question_answering_quality/mean']*20:.1f}%")
    export_results(baseline_model, baseline_results, candidate_model, candidate_results, f'eval_results_{timestamp}.json')
    
def export_results(baseline_model: str, baseline_results: EvalResult, candidate_model: str, candidate_results: EvalResult, file_name: str):
    '''Export combined results of the two eval runs to a single JSON file that can be visualized in LLM Comparator.'''
    with open(file_name, 'w') as f:
        f.write(json.dumps(dict(
            models=[dict(name=baseline_model), dict(name=candidate_model)],
            examples=combine_eval_runs(baseline_results, candidate_results),
            metadata={'custom_fields_schema':[]}
        )))
    print(f"Evaluation results saved to {file_name} in LLM Comparator format: https://pair-code.github.io/llm-comparator/")

def combine_eval_runs(baseline: EvalResult, candidate: EvalResult) -> list[dict]:
    '''Combine the evaluation results for the two models and calculate the pairwise score.'''
    if None in [baseline, candidate] or len(baseline.metrics_table.index) != len(candidate.metrics_table.index):
        raise ValueError(f'Invalid eval results!')
    examples = []
    for b, c in zip(baseline.metrics_table.to_dict(orient='records'), candidate.metrics_table.to_dict(orient='records')):
        score_b = b.get('question_answering_quality/score')
        score_c = c.get('question_answering_quality/score')
        examples.append(dict(
            input_text=b.get('prompt'),
            output_text_a=b.get('response').strip(),
            output_text_b=c.get('response').strip(),
            score = 0 if score_b == score_c else 1.0 if score_b > score_c else -1.0,
            tags=[],
            individual_rater_scores=[]
        ))
    return examples

if __name__ == '__main__':
    if os.getenv('PROJECT_ID', 'your-project-id') == 'your-project-id':
        raise ValueError('Please configure your Google Cloud Project ID.')
    vertexai.init(project=os.getenv('PROJECT_ID'), location='us-central1')
    run_eval(
        experiment_name = 'eval-document-qna-demo',
        baseline_model = 'gemini-1.5-flash-001',
        candidate_model = 'gemini-2.0-flash-001',
        prompt_template_local_path = 'prompt_template.txt',
        dataset_local_path = 'dataset.jsonl'    
    )