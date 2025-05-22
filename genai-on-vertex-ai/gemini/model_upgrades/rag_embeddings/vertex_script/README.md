# RAG Retrieval

### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of two embedding models on a RAG dataset using [Vertex AI Evaluation Service](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview).

We will be looking at `text-embedding-004` as our baseline model and `text-embedding-005` as our candidate model. Please follow the [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings) here to get an understanding of the various text embedding models. 

- Use case: RAG retrieval

- Metric: This eval uses a Pointwise Retrieval quality template to evaluate the responses and pick a model as the winner. We will define `retrieval quality` as the metric here. It checks whether the `retrieved_context` contains all the key information present in `reference`.

- Evaluation Datasets are based on [RAG Dataset](https://www.kaggle.com/datasets/samuelmatsuoharris/single-topic-rag-evaluation-dataset) in compliance with the following [license](https://www.mit.edu/~amini/LICENSE.md). They include 8 randomly sampled prompts in JSONL files `baseline_dataset.jsonl` and `candidate_dataset.jsonl` with the following structure:
    - `question`: User inputted question 
    - `reference`: The golden truth answer for the question
    - `retrieved_context`: The context retrieved from the model.

- Prompt Template is a zero-shot prompt located in [`prompt_template.txt`](./prompt_template.txt) with two prompt variables ( `reference` and `retrieved_context`) that are automatically populated from our dataset.

- This eval recipe uses an LLM judge model(gemini-2.0-flash) to evaluate the retrieval quality of the embedding models. 

### _Prerequisite_

This recipe assumes that the user has already created datasets for the baseline embedding model and the candidate embedding model. The user needs to generate the datasets for the baseline(text-embedding-004) and candidate(text-embedding-005) embedding models. Please refer to [RAG Engine generation notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/rag-engine/rag_engine_eval_service_sdk.ipynb) to create two separate RAG engines and set up corresponding datasets. The `retrieved_context` column in the dataset is the context retrieved from the respective RAG engine for each one of the questions.

- Python script [`eval.py`](./eval.py) configures the evaluation:
    - `run_eval`: configures the evaluation task, runs it on the 2 models and prints the results.
    - `load_dataset`: loads the dataset including the contents of all documents.

- Shell script [`run.sh`](./run.sh) installs the required Python libraries and runs `eval.py` 

- Google Cloud Shell is the easiest option as it automatically clones our Github repo:

    <a href="https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples&cloudshell_git_branch=main&cloudshell_workspace=genai-on-vertex-ai/gemini/model_upgrades">
        <img alt="Open in Cloud Shell" src="http://gstatic.com/cloudssh/images/open-btn.png">
    </a>

- Alternatively, you can use the following command to clone this repo to any Linux environment with configured [Google Cloud Environment](https://cloud.google.com/vertex-ai/docs/start/cloud-environment):

    ``` bash
    git clone --filter=blob:none --sparse https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples.git && \
    cd applied-ai-engineering-samples && \
    git sparse-checkout init && \
    git sparse-checkout set genai-on-vertex-ai/gemini/model_upgrades && \
    git pull origin main
    cd genai-on-vertex-ai/gemini/model_upgrades
    ```

1. Navigate to the Eval Recipe directory in terminal, set your Google Cloud Project ID and run the shell script `run.sh`.

    ``` bash
    cd rag_embeddings/vertex_script
    export PROJECT_ID="[your-project-id]"
    ./run.sh
    ```

1. The resulting metrics will be displayed in the script output. 

1. You can use [Vertex AI Experiments](https://console.cloud.google.com/vertex-ai/experiments) to view the history of evaluations for each experiment, including the final metrics scores.

## How to customize this Eval Recipe:

We will have two runs, one for the baseline model and the candidate model

1. Edit the Python script `eval.py`:
    - set the `project` parameter of vertexai.init to your Google Cloud Project ID.
    - set the parameter `model`  in the run_eval calls (e.g., 'gemini-2.0-flash') to the LLM you want to use for performing the evaluation task.
    - set the parameter `embedding_model` to the model that you want to run the evaluation for
    - configure a unique `experiment_name` for tracking purposes
    - set the parameter `dataset_local_path` to the file you are running the evaluations for 
1. Replace the contents of `prompt_template.txt` with your custom prompt template. Make sure that prompt template variables map to the dataset attributes.
1. Please refer to our [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval) if you want to further customize your evaluation. Vertex AI Evaluation Service has a lot of features that are not included in this recipe.