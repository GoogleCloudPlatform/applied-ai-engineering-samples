# Instruction Following
### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of an Instruction Following prompt with Gemini 1.5 Flash and Gemini 2.0 Flash using  [Vertex AI Evaluation Service](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview).

[Instruction-Following Eval (IFEval)](https://arxiv.org/abs/2311.07911) is a straightforward and easy-to-reproduce evaluation benchmark. It focuses on a set of "verifiable instructions" such as "write in more than 400 words", "write in bullet points", etc. 

- Use case: Instruction Following 

- Evaluation Dataset is based on [Instruction Following Evaluation Dataset](https://github.com/google-research/google-research/blob/master/instruction_following_eval/data/input_data.jsonl). It includes 10 randomly sampled prompts in a JSONL file `dataset.jsonl` with the follwing structure:
    - `prompt`: The task with specific instructions provided

- Prompt Template is a zero-shot prompt located in [`prompt_template.txt`](./prompt_template.txt) with one prompt variable (`prompt`) that is automatically populated from our dataset.

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
    cd instruction-following/vertex_script
    export PROJECT_ID="[your-project-id]"
    ./run.sh
    ```

1. The resulting metrics will be displayed in the script output. 

1. You can use [Vertex AI Experiments](https://console.cloud.google.com/vertex-ai/experiments) to view the history of evaluations for each experiment, including the final metrics scores.

## How to customize this Eval Recipe:

1. Edit the Python script `eval.py`:
    - set the `project` parameter of vertexai.init to your Google Cloud Project ID.
    - set the parameter `baseline_model` to the model that is currently used by your application
    - set the parameter `candidate_model` to the model that you want to compare with your current model
    - configure a unique `experiment_name` for tracking purposes
1. Replace the contents of `dataset.jsonl` with your custom data in the same format.
1. Replace the contents of `prompt_template.txt` with your custom prompt template. Make sure that prompt template variables map to the dataset attributes.
1. Please refer to our [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval) if you want to further customize your evaluation. Vertex AI Evaluation Service has a lot of features that are not included in this recipe.