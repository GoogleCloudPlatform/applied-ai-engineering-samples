# Text Classification 

### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of a text classification prompt with Gemini 1.0 and Gemini 2.0 using  [Vertex AI Evaluation Service](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview).

![](diagram.png "Model Comparison Eval")

- Use case: given a Product Description find the most relevant Product Category from a predefined list of categories.

- Metric: this eval uses a single deterministic metric "Accuracy" calculated by comparing model responses with ground truth labels. 

- Labeled evaluation dataset ([`dataset.jsonl`](./dataset.jsonl)) is based on [MAVE](https://github.com/google-research-datasets/MAVE/tree/main) dataset from Google Research. It includes 6 records that represent products from different categories. Each record provides two attributes which are wrapped in the `vars` object. This dataset structure allows Promptfoo to recognize variables that are needed to populate prompt templates, and ground truth labels used for scoring:
    - `product`: product name and description
    - `reference`: the name of correct product category which serves as the ground truth label

- Prompt template is a zero-shot prompt located in [`prompt_template.txt`](./prompt_template.txt) with just one prompt variable `product` that maps to the `product` attribute in the dataset.

- Python script [`eval.py`](./eval.py) configures the evaluation:
    - `run_eval`: configures the evaluation task, runs it on the 2 models and prints the results.
    - `case_insensitive_match`: scores the accuracy of model responses by comparing them to ground truth labels.  

- Shell script [`run.sh`](./run.sh) installs the required Python libraries and runs `eval.py` 

## How to run this Eval Recipe

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
    cd text_classification/vertex_script
    export PROJECT_ID="[your-project-id]"
    ./run.sh
    ```

1. The resulting scores will be displayed in the script output. 
1. You can use [Vertex AI Experiments](https://console.cloud.google.com/vertex-ai/experiments) to view the history of evaluations for each experiment, including the final metrics scores.

## How to customize this Eval Recipe:

1. Edit the Python script `eval.py`:
    - set the `project` parameter of vertexai.init to your Google Cloud Project ID.
    - set the parameter `baseline_model` to the model that is currently used by your application
    - set the parameter `candidate_model` to the model that you want to compare with your current model
    - configure a unique `experiment_name` for each template for tracking purposes
1. Replace the contents of `dataset.jsonl` with your custom data in the same format.
1. Replace the contents of `prompt_template.txt` with your custom prompt template. Make sure that prompt template variables have the same names as dataset attributes.
1. Please refer to our [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval) if you want to further customize your evaluation. Vertex AI Evaluation Service has a lot of features that are not included in this recipe, including LLM-based autoraters that can provide valuable metrics even without ground truth labels.
    



