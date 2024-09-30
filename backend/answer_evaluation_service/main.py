# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import uuid
from datetime import datetime
from typing import Any

import functions_framework
import nest_asyncio
import pandas as pd
from flask import jsonify
from vertexai.evaluation import EvalTask, MetricPromptTemplateExamples

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nest_asyncio.apply()


@functions_framework.http
def evaluate_rag_answer(request) -> Any:
    """
    Evaluate a RAG (Retrieval-Augmented Generation) answer using Vertex AI.

    Args:
        request: The HTTP request object containing the query, context, and answer.

    Returns:
        Dict[str, Any]: A dictionary containing the evaluation metrics.
    """
    request_data = request.get_json()
    queries = request_data["queries"]
    contexts = request_data["contexts"]
    answers = request_data["answers"]

    # logger.info(f"Evaluating RAG answer for query: {query}")

    eval_dataset = pd.DataFrame(
        {
            "prompt": [
                f"""Answer the question based only on the following context: {context}
                Question: {query}"""
                for context, query in zip(contexts, queries)
            ],
            "response": answers,
        }
    )

    # Generate a unique experiment name using UUID
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    experiment = f"rag-eval-{timestamp}-{unique_id}"

    logger.info(f"Created experiment: {experiment}")

    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=[
            MetricPromptTemplateExamples.Pointwise.QUESTION_ANSWERING_QUALITY,
            MetricPromptTemplateExamples.Pointwise.INSTRUCTION_FOLLOWING,
            # MetricPromptTemplateExamples.Pointwise.GROUNDEDNESS,
        ],
        experiment=experiment,
    )

    logger.info("Starting evaluation task")
    result = eval_task.evaluate(
        experiment_run_name=experiment, evaluation_service_qps=100
    )

    fields_to_remove = {"prompt", "response"}
    metrics_list = result.metrics_table.to_dict(orient="records")

    # Use dictionary comprehension inside a list comprehension to exclude unwanted fields
    metrics_list = [
        {k: v for k, v in metric_dict.items() if k not in fields_to_remove}
        for metric_dict in metrics_list
    ]

    print(f"Evaluation metrics: {metrics_list}")
    return jsonify({"metrics": metrics_list})
