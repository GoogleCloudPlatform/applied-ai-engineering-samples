# Needle In A Haystack - Pressure Testing LLMs

This repository is a fork of [Greg Kamradt's](https://twitter.com/GregKamradt) code. 

Original Repository: https://github.com/gkamradt/LLMTest_NeedleInAHaystack

This fork adds support for using **Google Gemini** (and only Google Gemini) models as the provider and evaluator.

It also differs in that the needle behavior matches that used in the [Gemini 1.5 paper](https://arxiv.org/pdf/2403.05530). Quoting from the paper:

> We insert a needle at linearly spaced intervals from the beginning to the end of the context, where
the needle is i.e., “The special magic {city} number is: {number}” where the city and
number are varied for each query, and query the model to return the magic number for a specific
city.

This dynamic needle is prevent false positives from caching. To revert to the original static needle behavior use `--dynamic_needle=False`



## The Test

1. Place a random fact or statement (the 'needle') in the middle of a long context window (the 'haystack')
2. Ask the model to retrieve this statement
3. Iterate over various document depths (where the needle is placed) and context lengths to measure performance


## Getting Started

### Setup Virtual Environment

We recommend setting up a virtual environment to isolate Python dependencies, ensuring project-specific packages without conflicting with system-wide installations.

```zsh
python3 -m venv venv
source venv/bin/activate
```

### Install Requirements

```zsh
pip install -e .
```

### Quickstart

```zsh
needlehaystack.run_test --gcp_project_id <YOUR_PROJECT_ID>  --document_depth_percents "[50]" --context_lengths "[200]"
```

### Detailed Instructions

Start using the package by calling the entry point `needlehaystack.run_test` from command line.

You can then run the analysis with the following command line arguments:

- `gcp_project_id` - The GCP project ID used to run the test. 
- `model_name` - Model name of the language model accessible by the provider. Defaults to `gemini-1.5-pro`
- `evaluator_model_name` - Model name of the language model accessible by the evaluator. Defaults to `gemini-1.5-pro`
- `dynamic_needle` - Whether to use the dynamic needle or not. Defaults to `True`
- `needle` - The statement or fact which will be placed in your context. Only used if `dynamic_needle=False`
- `haystack_dir` - The directory which contains the text files to load as background context. Only text files are supported
- `retrieval_question` - The question with which to retrieve your needle in the background context
- `results_version` - You may want to run your test multiple times for the same combination of length/depth, change the version number if so
- `num_concurrent_requests` - Default: 1. Set higher if you'd like to run more requests in parallel. Keep in mind rate limits.
- `save_results` - Whether or not you'd like to save your results to file. They will be temporarily saved in the object regardless. True/False. If `save_results = True`, then this script will populate a `result/` directory with evaluation information. Due to potential concurrent requests each new test will be saved as a few file.
- `save_contexts` - Whether or not you'd like to save your contexts to file. **Warning** these will get very long. True/False
- `final_context_length_buffer` - The amount of context to take off each input to account for system messages and output tokens. This can be more intelligent but using a static value for now. Default 200 tokens.
- `context_lengths_min` - The starting point of your context lengths list to iterate
- `context_lengths_max` - The ending point of your context lengths list to iterate
- `context_lengths_num_intervals` - The number of intervals between your min/max to iterate through
- `context_lengths` - A custom set of context lengths. This will override the values set for `context_lengths_min`, max, and intervals if set
- `document_depth_percent_min` - The starting point of your document depths. Should be int > 0
- `document_depth_percent_max` - The ending point of your document depths. Should be int < 100
- `document_depth_percent_intervals` - The number of iterations to do between your min/max points
- `document_depth_percents` - A custom set of document depths lengths. This will override the values set for `document_depth_percent_min`, max, and intervals if set
- `document_depth_percent_interval_type` - Determines the distribution of depths to iterate over. 'linear' or 'sigmoid
- `seconds_to_sleep_between_completions` - Default: None, set # of seconds if you'd like to slow down your requests
- `print_ongoing_status` - Default: True, whether or not to print the status of test as they complete

`LLMMultiNeedleHaystackTester` parameters:

- `multi_needle` - True or False, whether to run multi-needle
- `needles` - List of needles to insert in the context


## Multi Needle Evaluator

To enable multi-needle insertion into our context, use `--multi_needle True`.

This inserts the first needle at the specified `depth_percent`, then evenly distributes subsequent needles through the remaining context after this depth.

For even spacing, it calculates the `depth_percent_interval` as:

```
depth_percent_interval = (100 - depth_percent) / len(self.needles)
```

So, the first needle is placed at a depth percent of `depth_percent`, the second at `depth_percent + depth_percent_interval`, the third at `depth_percent + 2 * depth_percent_interval`, and so on.

Following example shows the depth percents for the case of 10 needles and depth_percent of 40%.

```
depth_percent_interval = (100 - 40) / 10 = 6

Needle 1: 40
Needle 2: 40 + 6 = 46
Needle 3: 40 + 2 * 6 = 52
Needle 4: 40 + 3 * 6 = 58
Needle 5: 40 + 4 * 6 = 64
Needle 6: 40 + 5 * 6 = 70
Needle 7: 40 + 6 * 6 = 76
Needle 8: 40 + 7 * 6 = 82
Needle 9: 40 + 8 * 6 = 88
Needle 10: 40 + 9 * 6 = 94
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details. Use of this software requires attribution to the original author and project, as detailed in the license.
