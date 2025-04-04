# Text Classification 
### _Eval Recipe for model migration_

This Eval Recipe demonstrates how to compare performance of a text classification prompt with Gemini 1.0 and Gemini 2.0 using a labeled dataset and open source evaluation tool [Promptfoo](https://www.promptfoo.dev/).

![](diagram.png "Promptfoo")

- Use case: given a Product Description find the most relevant Product Category from a predefined list of categories.

- Metric: this eval uses a single deterministic metric "Accuracy" calculated by comparing model responses with ground truth labels. 

- Labeled evaluation dataset (dataset.jsonl) includes 6 records that represent products from different categories. Each record provides two attributes which are wrapped in the `vars` object. This dataset structure allows Promptfoo to recognize variables that are needed to populate prompt templates, and ground truth labels used for scoring:
    - `product`: product name and description
    - `category`: the name of correct product category which serves as the ground truth label

- Prompt template is a zero-shot prompt located in prompt_template.txt with just one prompt variable `product` that maps to the `product` attribute in the dataset.

- promptfooconfig.yaml contains all Promptfoo configuration:
    - `providers`: list of models that will be evaluated
    - `prompts`: location of the prompt template file
    - `tests`: location of the labeled dataset file
    - `defaultTest`: defines how we calculate the Accuracy:
        1. `transform: output.trim()` removes any white space around the model response
        1. `type: equals` scores model responses based on exact match with ground truth labels
        1. `value: "{{category}}"` instructs Promptfoo to use the "category" attribute in our dataset as the ground truth label


- To install Promptfoo follow [these instructions](https://www.promptfoo.dev/docs/installation/).
- Run the evaluation in command line: `promptfoo eval`
- View detailed results in browser: `promptfoo view`. You can switch the Display option to `Show failures only` in order to investigate underperforming prompts.
- How to customize this Eval Recipe:
    1. Copy the configuration file (promptfooconfig.yaml) to a new folder in your source code repo
    1. Create your own labeled dataset file with JSONL schema similar to dataset.jsonl 
    1. Save your prompt template to prompt_template.txt and make sure that the template variables map to the variables defined in your dataset.
    1. That's it! You are ready to run `promptfoo eval`. If needed, add alternative prompt templates or additional metrics to promptfooconfig.yaml as explained [here](https://www.promptfoo.dev/docs/configuration/parameters/).



