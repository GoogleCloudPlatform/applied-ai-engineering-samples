-- Configuration Tables
-- eval_tasks
CREATE TABLE IF NOT EXISTS eval_tasks (
    task_id                     STRING OPTIONS(description="Unique identifier for the evaluation task"),
    task_desc                   STRING OPTIONS(description="Description of the evaluation task"),
    create_datetime             DATETIME OPTIONS(description="Timestamp of when the task was created"),
    update_datetime             DATETIME OPTIONS(description="Timestamp of when the task was last updated"),
    tags                        ARRAY<STRING> OPTIONS(description="Tags associated with the task for easy filtering and searching"),
    metadata                    STRING OPTIONS(description="Additional metadata related to the task")
) 
OPTIONS(
    description="Table storing information about different Generative AI tasks to be evaluated",
    labels=[("tool", "vertexai-gemini-evals")]
);

-- eval_experiments
CREATE TABLE IF NOT EXISTS eval_experiments (
    experiment_id               STRING OPTIONS(description="Unique identifier for the evaluation experiment"),
    experiment_desc             STRING OPTIONS(description="Description of the evaluation experiment"),
    task_id                     STRING OPTIONS(description="Foreign key referencing the eval_tasks table, linking the experiment to its corresponding task"),
    eval_dataset_id             STRING OPTIONS(description="Foreign key referencing the eval_datasets table, linking the experiment to its dataset"),
    prompt_id                   STRING OPTIONS(description="Foreign key referencing the eval_prompts table, linking the experiment to its prompt"),
    model_endpoint              STRING OPTIONS(description="The endpoint of the model being evaluated"),
    model_name                  STRING OPTIONS(description="The name of the model being evaluated"),
    generation_config           STRING OPTIONS(description="JSON string containing the model generation configuration"),
    is_streaming                BOOL OPTIONS(description="Indicates whether the evaluation is streaming or not"),
    safety_settings             STRING OPTIONS(description="JSON string containing the safety settings for the evaluation"),
    metric_config               STRING OPTIONS(description="JSON string containing the configuration for the metrics used in the evaluation"),
    create_datetime             DATETIME OPTIONS(description="Timestamp of when the experiment was created"),
    update_datetime             DATETIME OPTIONS(description="Timestamp of when the experiment was last updated"),
    elapsed_time                NUMERIC OPTIONS(description="Total time taken for the experiment to complete"),
    tags                        ARRAY<STRING> OPTIONS(description="Tags associated with the experiment for easy filtering and searching"),
    metadata                    STRING OPTIONS(description="Additional metadata related to the experiment")
) 
OPTIONS(
    description="Table storing information about evaluation experiments conducted on different tasks",
    labels=[("tool", "vertexai-gemini-evals")]
);

-- eval_prompts
CREATE TABLE IF NOT EXISTS eval_prompts (
    prompt_id                   STRING OPTIONS(description="Unique identifier for the prompt"),
    prompt_description          STRING OPTIONS(description="Description of the prompt"),
    system_instruction          STRING OPTIONS(description="System instructions provided to the model before the prompt"),
    prompt_template             STRING OPTIONS(description="Template used to construct the prompt"),
    prompt_type                 STRING OPTIONS(description="Type of prompt (e.g., single-turn, chat)"),
    contents                    STRING OPTIONS(description="Array of prompt contents"),
    tools                       STRING OPTIONS(description="Array of function declarations for tools used in the prompt"),
    tool_config                 STRING OPTIONS(description="Configuration for the tools used in the prompt"),
    is_multimodal               BOOL OPTIONS(description="Indicates whether the prompt is multimodal or not"),
    version_num                 STRING OPTIONS(description="Version number of the prompt"),
    create_datetime             DATETIME OPTIONS(description="Timestamp of when the prompt was created"),
    update_datetime             DATETIME OPTIONS(description="Timestamp of when the prompt was last updated"),
    tags                        ARRAY<STRING> OPTIONS(description="Tags associated with the prompt for easy filtering and searching"),
    metadata                    STRING OPTIONS(description="Additional metadata related to the prompt")
) 
OPTIONS(
    description="Table storing information about different prompts used in evaluations",
    labels=[("tool", "vertexai-gemini-evals")]
);

-- eval_datasets
CREATE TABLE IF NOT EXISTS eval_datasets (
    dataset_id                  STRING OPTIONS(description="Unique identifier for the evaluation dataset"),
    dataset_desc                STRING OPTIONS(description="Description of the evaluation dataset"),
    dataset_format              STRING OPTIONS(description="Format of the evaluation dataset (e.g., JSON, CSV)"),
    dataset_location            STRING OPTIONS(description="Location of the evaluation dataset (e.g., GCS bucket)"),
    reference_column_name       STRING OPTIONS(description="Name of the column in the dataset containing the reference/ground truth data"),
    create_datetime             DATETIME OPTIONS(description="Timestamp of when the dataset was created"),
    update_datetime             DATETIME OPTIONS(description="Timestamp of when the dataset was last updated")
) 
OPTIONS(
    description="Table storing references to evaluation datasets used in experiments",
    labels=[("tool", "vertexai-gemini-evals")]
);

-- eval_runs
CREATE TABLE IF NOT EXISTS eval_runs (
    run_id                      STRING OPTIONS(description="Unique identifier for the evaluation run"),
    experiment_id               STRING OPTIONS(description="Foreign key referencing the eval_experiments table, linking the run to its corresponding experiment"),
    task_id                     STRING OPTIONS(description="Foreign key referencing the eval_tasks table, linking the run to its corresponding task"),
    example_id                  STRING OPTIONS(description="Identifier for the specific example within the dataset used in this run"),
    system_instruction          STRING OPTIONS(description="System instructions provided to the model before the input prompt"),
    input_prompt                STRING OPTIONS(description="The input prompt used in the evaluation run"),
    output_text                 STRING OPTIONS(description="The text output generated by the model"),
    output_response             STRING OPTIONS(description="The complete response generated by the model, including any structured data"),
    metrics                     STRING OPTIONS(description="JSON string containing the metrics and their scores for this run"),
    total_elapsed_time          NUMERIC OPTIONS(description="Total time taken for this run to complete"),
    avg_latency_per_request     NUMERIC OPTIONS(description="Average latency per request in this run"),
    avg_output_token_count      INT OPTIONS(description="Average number of output tokens generated in this run"),
    total_input_token_count     INT OPTIONS(description="Total number of input tokens in this run"),
    total_output_token_count    INT OPTIONS(description="Total number of output tokens generated in this run"),
    total_total_token_count     INT OPTIONS(description="Total number of tokens (input + output) in this run"),
    create_datetime             DATETIME OPTIONS(description="Timestamp of when the run was created"),
    update_datetime             DATETIME OPTIONS(description="Timestamp of when the run was last updated"),
    tags                        ARRAY<STRING> OPTIONS(description="Tags associated with the run for easy filtering and searching"),
    metadata                    STRING OPTIONS(description="Additional metadata related to the run")
)
OPTIONS(
    description="Table storing information about individual evaluation runs within experiments",
    labels=[("tool", "vertexai-gemini-evals")]
);

-- Results
-- eval_run_details
CREATE TABLE IF NOT EXISTS eval_run_details (
    run_id                      STRING OPTIONS(description="Unique identifier for the evaluation run, referencing the eval_runs table"),
    experiment_id               STRING OPTIONS(description="Foreign key referencing the eval_experiments table, linking the run details to its corresponding experiment"),
    task_id                     STRING OPTIONS(description="Foreign key referencing the eval_tasks table, linking the run details to its corresponding task"),
    example_id                  STRING OPTIONS(description="Identifier for the specific example within the dataset used in this run"),
    system_instruction          STRING OPTIONS(description="System instructions provided to the model before the input prompt"),
    input_prompt                STRING OPTIONS(description="The input prompt used in the evaluation run"),
    output_text                 STRING OPTIONS(description="The text output generated by the model"),
    output_response             STRING OPTIONS(description="The complete response generated by the model, including any structured data"),
    ground_truth                STRING OPTIONS(description="The expected/correct output for the given input"),
    metrics                     STRING OPTIONS(description="JSON string containing the metrics and their scores for this run"),
    input_token_count           INT OPTIONS(description="Number of input tokens in this run"),
    output_token_count          INT OPTIONS(description="Number of output tokens generated in this run"),
    total_token_count           INT OPTIONS(description="Total number of tokens (input + output) in this run"),
    num_retries                 INT OPTIONS(description="Number of retries attempted for this run"),
    avg_latency                 NUMERIC OPTIONS(description="Average latency for this run"),
    latencies                   ARRAY<NUMERIC> OPTIONS(description="Array of latencies for each request in this run"),
    create_datetime             DATETIME OPTIONS(description="Timestamp of when the run details were created"),
    update_datetime             DATETIME OPTIONS(description="Timestamp of when the run details were last updated"),
    tags                        ARRAY<STRING> OPTIONS(description="Tags associated with the run details for easy filtering and searching"),
    metadata                    STRING OPTIONS(description="Additional metadata related to the run details")
) 

OPTIONS(
    description="Table storing detailed information about individual evaluation runs, including ground truth and latencies",
    labels=[("tool", "vertexai-gemini-evals")]
);

ALTER TABLE eval_tasks ALTER COLUMN create_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_tasks ALTER COLUMN update_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_experiments ALTER COLUMN create_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_experiments ALTER COLUMN update_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_prompts ALTER COLUMN create_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_prompts ALTER COLUMN update_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_datasets ALTER COLUMN create_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_datasets ALTER COLUMN update_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_runs ALTER COLUMN create_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_runs ALTER COLUMN update_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_run_details ALTER COLUMN create_datetime SET DEFAULT (CURRENT_DATETIME());
ALTER TABLE eval_run_details ALTER COLUMN update_datetime SET DEFAULT (CURRENT_DATETIME());