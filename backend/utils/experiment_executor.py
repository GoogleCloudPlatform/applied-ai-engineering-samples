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

import json
import logging
import time
from typing import Any
from google.cloud.workflows import executions_v1
from .firestore_utils import get_config_section

logger = logging.getLogger(__name__)

# Get config from Firebase
cloud_workflows_config = get_config_section("cloud_workflows")
PROJECT_ID = cloud_workflows_config.get("project_id")
LOCATION = cloud_workflows_config.get("location")
WORKFLOW_NAME = cloud_workflows_config.get("workflow_name")


# TODO:add appropriate stricter type hints
def execute_workflow(tasks: Any) -> Any:
  """Execute the workflow with the given tasks.

  Args:
      tasks (List[Dict[str, str]]): A list of tasks to be executed in the
        workflow.

  Returns:
      List[Dict]: The results of the workflow execution.

  Raises:
      Exception: If the workflow execution fails.
  """
  execution_client = executions_v1.ExecutionsClient()
  workflow_path = (
      f"projects/{PROJECT_ID}/locations/{LOCATION}/workflows/{WORKFLOW_NAME}"
  )

  for task in tasks:
    if "model_params" in task and isinstance(task["model_params"], dict):
      task["model_params"] = {
          k: v for k, v in task["model_params"].items() if v is not None
      }

  argument = json.dumps({"tasks": tasks})

  logger.info(f"Starting workflow execution for {len(tasks)} tasks")
  execution = execution_client.create_execution(
      request={"parent": workflow_path, "execution": {"argument": argument}}
  )

  execution_name = execution.name

  while True:
    execution = execution_client.get_execution(request={"name": execution_name})
    if execution.state != executions_v1.Execution.State.ACTIVE:
      break
    time.sleep(5)  # Wait for 5 seconds before checking again

  if execution.state == executions_v1.Execution.State.SUCCEEDED:
    logger.info("Workflow execution completed successfully")
    return json.loads(execution.result)
  else:
    logger.error(f"Workflow execution failed with state: {execution.state}")
    logger.error(f"Error: {execution.error}")
    raise Exception("Workflow execution failed")


def process_workflow_results(results: Any) -> Any:
  """Process the results of the workflow execution, including only successful tasks.

  Args:
      results (List[Dict]): The raw results from the workflow execution.

  Returns:
      List[Dict]: Processed results containing only successful tasks.
  """
  processed_results = []
  for result in results:
    if result.get("success", False):
      processed_result = {
          "model_name": result.get("model_name"),
          "retriever_name": result.get("retriever_name"),
          "answer": result.get("answer_gen_result", {}).get("answer", "N/A"),
          "eval_result": result.get("eval_service_result", {}),
          "query": result.get("query"),
      }
      processed_results.append(processed_result)
    else:
      logger.warning(f"Task failed: {result.get('error', 'Unknown error')}")

  if not processed_results:
    logger.warning("No successful tasks to process")

  logger.info(f"Processed {len(processed_results)} successful results")
  return processed_results
