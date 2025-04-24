# Instruction Following 
### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of an Instruction Following prompt with Gemini 1.5 Flash and Gemini 2.0 Flash using an unlabeled dataset and open source evaluation tool [Promptfoo](https://www.promptfoo.dev/).

[Instruction-Following Eval (IFEval)](https://arxiv.org/abs/2311.07911) is a straightforward and easy-to-reproduce evaluation benchmark. It focuses on a set of "verifiable instructions" such as "write in more than 400 words", "write in bullet points", etc. 

- Use case: Instruction Following 

- Evaluation Dataset is based on [Instruction Following Evaluation Dataset](https://github.com/google-research/google-research/blob/master/instruction_following_eval/data/input_data.jsonl). It includes 15 randomly sampled prompts in a JSONL file `dataset.jsonl`. Each record in this file includes 1 attribute wrapped in the `vars` object. This structure allows Promptfoo to specify the variables needed to populate prompt templates (document and question), as well as the ground truth label required to score the accuracy of model responses:
    - `prompt`: The task with specific instructions provided

- Prompt Template is a zero-shot prompt located in [`prompt_template.txt`](./prompt_template.txt) with one prompt variable (`prompt`) that is automatically populated from our dataset.

- [`promptfooconfig.yaml`](./promptfooconfig.yaml) contains all Promptfoo configuration:
    - `providers`: list of models that will be evaluated
    - `prompts`: location of the prompt template file
    - `tests`: location of the labeled dataset file
    - `defaultTest`: defines the scoring logic:
        `type: answer-relevance` The answer-relevance assertion evaluates whether an LLM's output is relevant to the original query. It uses a combination of embedding similarity and LLM evaluation to determine relevance..
        `value: "Check if the response adheres to the instructions in the prompt"` instructs Promptfoo to verify and score based on how well the generated response is aligned with the original prompt.
        `threshold: 0.5` Mark any responses with a score below 0.5 as a failure.



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

1. Install Promptfoo using [these instructions](https://www.promptfoo.dev/docs/installation/).
1. Navigate to the Eval Recipe directory in terminal and run the command `promptfoo eval`.

``` bash
cd genai-on-vertex-ai/gemini/model_upgrades/instruction-following/promptfoo
promptfoo eval
```
1. Run `promptfoo view` to analyze the eval results. You can switch the Display option to `Show failures only` in order to investigate any underperforming prompts.

## How to customize this Eval Recipe:
1. Copy the configuration file `promptfooconfig.yaml` to a new folder.
1. Add your labeled dataset file with JSONL schema similar to `dataset.jsonl`. 
1. Save your prompt template to `prompt_template.txt` and make sure that the template variables map to the variables defined in your dataset.
1. That's it! You are ready to run `promptfoo eval`. If needed, add alternative prompt templates or additional metrics to promptfooconfig.yaml as explained [here](https://www.promptfoo.dev/docs/configuration/parameters/).