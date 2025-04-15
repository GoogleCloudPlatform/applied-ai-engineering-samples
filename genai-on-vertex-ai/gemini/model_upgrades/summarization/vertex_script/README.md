# Summarization
### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of a summarization prompt with Gemini 1.0 and Gemini 2.0 using  [Vertex AI Evaluation Service](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview).

![](diagram.png "Model Comparison Eval")

- Use case: summarize a news article.

- Use case: summarize a news article.

- The Evaluation Dataset[^1] includes 5 news articles stored as plain text files, and a JSONL file with ground truth labels: [`dataset.jsonl`](./dataset.jsonl). Each record in this file includes 2 attributes:
    - `document`: relative path to the plain text file containing the news article
    - `reference`: ground truth label (short summary of the article)

- Prompt Template is a zero-shot prompt located in [`prompt_template.txt`](./prompt_template.txt) with variable `document` that gets populated from the corresponding dataset attribute.

- Python script [`eval.py`](./eval.py) configures the evaluation:
    - `run_eval`: configures the evaluation task, runs it on the 2 models and prints the results.
    - `load_dataset`: loads the dataset including the contents of all documents.

- Shell script [`run.sh`](./run.sh) installs the required Python libraries and runs `eval.py` 

## How to run this Eval Recipe

1. Configure your [Google Cloud Environment](https://cloud.google.com/vertex-ai/docs/start/cloud-environment) and clone this Github repo to your environment. We recommend [Cloud Shell](https://shell.cloud.google.com/) or [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/workbench/instances/introduction).

``` bash
git clone --filter=blob:none --sparse https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples.git && \
cd applied-ai-engineering-samples && \
git sparse-checkout init && \
git sparse-checkout set genai-on-vertex-ai/gemini/model_upgrades && \
git pull origin main
```

2. Navigate to the Eval Recipe directory in terminal, set your Google Cloud Project ID and run the shell script `run.sh`.

``` bash
cd genai-on-vertex-ai/gemini/model_upgrades/summarization/vertex_script
export PROJECT_ID="[your-project-id]"
./run.sh
```

3. The resulting metrics will be displayed in the script output. You can find the prompts and model responses stored in `candidate_results.metrics_table`.
4. You can use [Vertex AI Experiments](https://console.cloud.google.com/vertex-ai/experiments) to view the history of evaluations for each experiment, including the final metrics scores.

## How to customize this Eval Recipe:

1. Edit the Python script `eval.py`:
    - set the `project` parameter of vertexai.init to your Google Cloud Project ID.
    - set the parameter `baseline_model` to the model that is currently used by your application
    - set the parameter `candidate_model` to the model that you want to compare with your current model
    - configure a unique `experiment_name` for tracking purposes
1. Replace the contents of `dataset.jsonl` with your custom data in the same format.
1. Replace the contents of `prompt_template.txt` with your custom prompt template. Make sure that prompt template variables map to the dataset attributes.
1. Please refer to our [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval) if you want to further customize your evaluation. Vertex AI Evaluation Service has a lot of features that are not included in this recipe.

[^1]: Dataset ([XSum](https://github.com/EdinburghNLP/XSum)) citation:
 @InProceedings{xsum-emnlp,
  author    = {Shashi Narayan and Shay B. Cohen and Mirella Lapata},
  title     = {Don't Give Me the Details, Just the Summary! {T}opic-Aware Convolutional Neural Networks for Extreme Summarization},
  booktitle = {Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing},
  year      = {2018},
  address   = {Brussels, Belgium},
}