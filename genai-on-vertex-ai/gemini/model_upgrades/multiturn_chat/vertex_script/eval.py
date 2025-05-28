import json
import os
import pandas as pd
import vertexai
from datetime import datetime
from google import genai
from google.genai.types import Content, Part
from vertexai.evaluation import EvalTask, MetricPromptTemplateExamples

def load_dataset(dataset_local_path: str) -> pd.DataFrame:
    '''Load conversation histories from local files to a Pandas DataFrame.'''
    with open(dataset_local_path, 'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    dataset = pd.DataFrame(data)
    dataset['history'] = dataset['chat_path'].apply(lambda chat_path: open(chat_path, 'r').read())
    return dataset[['history']]

def generate_chat_responses(project_id: str, location:str, model: str, dataset: pd.DataFrame, response_column_name: str) -> None:
    '''Generate the final model response for each conversation in the dataset using the specified model.'''
    client = genai.Client(vertexai=True, project=project_id, location=location)
    responses = []
    user_prompts = []
    for i, record in dataset.iterrows():
        print(f'Generating chat completion #{i+1} with {model}')
        messages = json.loads(record.get('history'))
        last_user_message = messages.pop()
        history = [
            Content(
                role=message['role'],
                parts=[Part(text=message['content'])],
            )
            for message in messages
        ]
        chat = client.chats.create(model=model, history=history)
        response = chat.send_message(message=[Part(text=last_user_message['content'])])
        user_prompts.append(last_user_message)
        responses.append( response.candidates[0].content.parts[0].text )
    dataset['prompt'] = user_prompts  # The last user message is required by the Autorater
    dataset[response_column_name] = responses 
    print(f'{len(responses)} responses from model {model} are stored in dataset column "{response_column_name}"')

def run_eval(project_id: str, location:str, experiment_name: str, baseline_model: str, candidate_model: str, dataset_local_path: str):
    '''Run a pairwise evaluation to compare the quality of model responses from the baseline and candidate models.'''
    vertexai.init(project=project_id, location=location)
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    dataset=load_dataset(dataset_local_path)
    generate_chat_responses(project_id, location, baseline_model, dataset, 'baseline_model_response')
    generate_chat_responses(project_id, location, candidate_model, dataset, 'response')
    task = EvalTask(
        dataset=dataset,
        metrics=[MetricPromptTemplateExamples.Pairwise.MULTI_TURN_CHAT_QUALITY],
        experiment=experiment_name
    )
    eval_results = task.evaluate(
        experiment_run_name=f"{timestamp}-{baseline_model.replace('.', '-')}"
    )
    print(f"Baseline model win rate: {eval_results.summary_metrics['pairwise_multi_turn_chat_quality/baseline_model_win_rate']:.2f}")
    print(f"Candidate model win rate: {eval_results.summary_metrics['pairwise_multi_turn_chat_quality/candidate_model_win_rate']:.2f}")

if __name__ == '__main__':
    if os.getenv('PROJECT_ID', 'your-project-id') == 'your-project-id':
        raise ValueError('Please configure your Google Cloud Project ID.')    
    run_eval(
        project_id=os.getenv('PROJECT_ID'),
        location=os.getenv('LOCATION') or 'us-central1',
        experiment_name = 'eval-multiturn-chat',
        baseline_model = 'gemini-1.5-flash-002',
        candidate_model = 'gemini-2.0-flash-001',
        dataset_local_path = 'dataset.jsonl'    
    )