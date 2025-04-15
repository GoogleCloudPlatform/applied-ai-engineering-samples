# Text Classification 

### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of a text classification prompt with Gemini 1.0 and Gemini 2.0 using a labeled dataset and open source evaluation tool [Promptfoo](https://www.promptfoo.dev/).

![](diagram.png "Promptfoo")

- Use case: given a Product Description find the most relevant Product Category from a predefined list of categories.

- Metric: this eval uses a single deterministic metric "Accuracy" calculated by comparing model responses with ground truth labels. 

- Labeled evaluation dataset ([`dataset.jsonl`](./dataset.jsonl)) is based on [MAVE](https://github.com/google-research-datasets/MAVE/tree/main) dataset from Google Research. It includes 6 records that represent products from different categories. Each record provides two attributes which are wrapped in the `vars` object. This dataset structure allows Promptfoo to recognize variables that are needed to populate prompt templates, and ground truth labels used for scoring:
    - `product`: product name and description
    - `category`: the name of correct product category which serves as the ground truth label

- Prompt template is a zero-shot prompt located in [`prompt_template.txt`](./prompt_template.txt) with just one prompt variable `product` that maps to the `product` attribute in the dataset.

- [`promptfooconfig.yaml`](./promptfooconfig.yaml) contains all Promptfoo configuration:
    - `providers`: list of models that will be evaluated
    - `prompts`: location of the prompt template file
    - `tests`: location of the labeled dataset file
    - `defaultTest`: defines how we calculate the Accuracy:
        1. `transform: output.trim()` removes any white space around the model response
        1. `type: equals` scores model responses based on exact match with ground truth labels
        1. `value: "{{category}}"` instructs Promptfoo to use the "category" attribute in our dataset as the ground truth label

## How to run this Eval Recipe

1. Configure your [Google Cloud Environment](https://cloud.google.com/vertex-ai/docs/start/cloud-environment) and clone this Github repo to your environment. We recommend [Cloud Shell](https://shell.cloud.google.com/) or [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/workbench/instances/introduction).

``` bash
git clone --filter=blob:none --sparse https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples.git && \
cd applied-ai-engineering-samples && \
git sparse-checkout init && \
git sparse-checkout set genai-on-vertex-ai/gemini/model_upgrades && \
git pull origin main
```

1. Install Promptfoo using [these instructions](https://www.promptfoo.dev/docs/installation/).

1. Navigate to the Eval Recipe directory in terminal and run the command `promptfoo eval`.

``` bash
cd genai-on-vertex-ai/gemini/model_upgrades/text_classification/promptfoo
promptfoo eval
```

1. Run `promptfoo view` to analyze the eval results. You can switch the Display option to `Show failures only` in order to investigate any underperforming prompts.

## How to customize this Eval Recipe:

1. Copy the configuration file `promptfooconfig.yaml` to a new folder.
1. Add your labeled dataset file with JSONL schema similar to `dataset.jsonl`. 
1. Save your prompt template to `prompt_template.txt` and make sure that the template variables map to the variables defined in your dataset.
1. That's it! You are ready to run `promptfoo eval`. If needed, add alternative prompt templates or additional metrics to promptfooconfig.yaml as explained [here](https://www.promptfoo.dev/docs/configuration/parameters/).

