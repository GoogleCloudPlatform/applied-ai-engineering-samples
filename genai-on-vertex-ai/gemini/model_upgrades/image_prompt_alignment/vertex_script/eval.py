import json
import os
import pandas as pd
import vertexai
from datetime import datetime
from google import genai
from google.genai.types import Content, Part
from vertexai.evaluation import EvalTask, EvalResult, CustomMetric

_AUTORATER_PROMPT_TEMPLATE = """
You are an expert image analyst with a keen eye for detail and a deep understanding of linguistics and human perception. 

# Definitions
- **Visually Groundable Requirement:** A specific claim or requirement within the image description that can be verified or refuted by examining the visual content of the image. This includes descriptions of objects (existence and attributes like color, size, shape, or text on the object), spatial relationships between objects, actions depicted, or overall scene characteristics like lighting conditions.
- **Gap:** A visually groundable requirement that is either contradicted by the image or cannot be directly confirmed based on the image.

# Instructions
Review the image and a description of that image located in the IMAGE_DESCRIPTION tag below.
Your goal is to rate the accuracy of the image description on the scale of 0 to 10.
You must use the following 6-step process and provide brief written notes for each step:
- Step 1. Identify all Visually Groundable Requirements contained in IMAGE_DESCRIPTION and save them to a numbered list. 
- Step 2. Write a numbered list of true/false questions that should be asked about each of the identified requirements in order to verify whether each requirement is satisfied by the image or not.
- Step 3. For each of the questions created in Step 2 write a brief analysis of the most relevant information in the provided image and then write the final answer:
    - True only if the image contains a clear positive answer to this question.
    - False if the image clearly justifies a negative answer to this question OR does not have enough information to answer this question.
- Step 4. Calculate the number of questions that received the answer "True" in step 3.
- Step 5. Calculate the final accuracy score as the percentage of positively answered questions out of the total questions answered in Step 3, rounded to the nearest integer.
- Step 6. Write the final answer as a Markdown codeblock containing a single JSON object with two attributes: 
    - "score" with the integer value of the final accuracy score calculated in Step 5.
    - "gaps" with a JSON array of strings that describe each gap (question that got a negative answer in Step 3). The description should be a one sentence statement that combines key information from the question and the analysis of relevant information from Step 3.

<IMAGE_DESCRIPTION>
{image_description}
</IMAGE_DESCRIPTION>

# Image Description accuracy analysis notes
## Step 1. IMAGE_DESCRIPTION contains the following Visually Groundable Requirements:
# """
_gemini_client = None

def load_dataset(dataset_local_path: str):
    """Convert the dataset to a Pandas DataFrame and load all images into the "image" column."""
    with open(dataset_local_path, "r") as file:
        data = [json.loads(line) for line in file if line.strip()]
    df = pd.DataFrame(data)
    df["image"] = df["image_path"].apply(lambda local_path: open(local_path, "rb").read())
    return df[["prompt", "image_path", "image"]]


def image_prompt_alignment_autorater(record: dict) -> dict:
    """Custom metric function for scoring prompt alignment between the image and prompt from the given dataset record."""
    response = _gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            Content(role="user", parts=[Part(text=_AUTORATER_PROMPT_TEMPLATE.format(image_description=record["prompt"]))]),
            Content(role="user", parts=[Part.from_bytes(data=record["image"], mime_type="image/jpeg")])
        ],
    )
    json_output = json.loads(response.text.split("```json\n")[1].split("\n```")[0])
    return {
        "image_prompt_alignment": json_output["score"],
        "explanation": json_output["gaps"],
    }


def run_eval(model: str, dataset_local_path: str):
    """Rate the alignment between image generation prompts and the generated images and identify gaps using a custom autorater."""
    timestamp = f"{datetime.now().strftime('%b-%d-%H-%M-%S')}".lower()
    dataset = load_dataset(dataset_local_path)
    task = EvalTask(
        dataset=dataset,
        metrics=[CustomMetric(name="image_prompt_alignment",metric_function=image_prompt_alignment_autorater)],
        experiment="image-prompt-alignment",
    )
    return task.evaluate(experiment_run_name=f"{timestamp}-{model.replace('.', '-')}")


def print_scores_and_explanations(title: str, eval_result: EvalResult) -> None:
    print(f'\n{"-"*80}\nRESULTS FOR {title}:')
    for i, row in eval_result.metrics_table.iterrows():
        gaps = row["image_prompt_alignment/explanation"]
        gaps = f', GAPS: {gaps}' if gaps else ''
        print(f'{row["image_path"]}: SCORE={row["image_prompt_alignment/score"]}%{gaps}')


def compare_models(project_id: str, location: str, model_a: str, dataset_path_a: str, model_b: str, dataset_path_b: str) -> None:
    global _gemini_client
    _gemini_client = genai.Client(vertexai=True, project=project_id, location=location)
    vertexai.init(project=project_id, location=location)
    results_a = run_eval(model_a, dataset_path_a)
    results_b = run_eval(model_b, dataset_path_b)
    print_scores_and_explanations(model_a, results_a)
    print_scores_and_explanations(model_b, results_b)
    print(f"\n{model_a} average alignment score = {results_a.summary_metrics['image_prompt_alignment/mean']:.1f}%")
    print(f"{model_b} average alignment score = {results_b.summary_metrics['image_prompt_alignment/mean']:.1f}%")


if __name__ == "__main__":
    if os.getenv("PROJECT_ID", "your-project-id") == "your-project-id":
        raise ValueError("Please configure your Google Cloud Project ID.")
    compare_models(
        project_id=os.getenv("PROJECT_ID"),
        location=os.getenv("LOCATION") or "us-central1",
        model_a="imagen2",
        dataset_path_a="dataset_imagen2.jsonl",
        model_b="imagen3",
        dataset_path_b="dataset_imagen3.jsonl",
    )