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

from fastapi import APIRouter, HTTPException
from google.cloud import firestore
from models.retriever_model import CompareRetrieverRequest, CompareRetrieverResponse
from utils.experiment_executor import execute_workflow, process_workflow_results

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

db = firestore.Client()


@router.get("/index-names")
def get_index_names():
  """Retrieve the names of all indices from Firestore.

  Returns:
      List[str]: A list of index names.
  """
  try:
    rp_indices = db.collection("rp_indices").get()
    index_names = [doc.id for doc in rp_indices]
    return {"index_names": index_names}
  except Exception as e:
    logger.exception("An error occurred while retrieving index names")
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-retrieval-results")
def compare_retrieval_results(
    data: CompareRetrieverRequest,
) -> CompareRetrieverResponse:
  """Compare retrieval results for different retriever-model pairs.

  Args:
      data (CompareRetrieverRequest): The request data containing
        retriever-model pairs and query information.

  Returns:
      CompareRetrieverResponse: The response containing the comparison results.

  Raises:
      HTTPException: If an error occurs during the workflow execution.
  """
  tasks = []
  for pair in data.retriever_model_pairs:
    for query in data.queries:
      base_task = {
          "retriever_name": pair.retriever_name,
          "query": query,
          "model_name": pair.model_name,
          "model_params": data.model_params[pair.model_name].dict(
              exclude_unset=True
          ),
          "index_name": data.index_name,
          "is_rerank": False,
      }
      tasks.append(base_task)

      if data.is_rerank:
        rerank_task = base_task.copy()
        rerank_task["is_rerank"] = True
        tasks.append(rerank_task)

  print(tasks)
  logger.info(f"Executing workflow with {len(tasks)} tasks")
  try:
    workflow_results = execute_workflow(tasks)
    processed_results = process_workflow_results(workflow_results)

    if not processed_results:
      logger.warning("No successful results to return")
      return CompareRetrieverResponse(results=[])

    logger.info(f"Successfully processed {len(processed_results)} results")
    return CompareRetrieverResponse(results=processed_results)

  except Exception as e:
    logger.exception("An error occurred while executing the workflow")
    raise HTTPException(status_code=500, detail=str(e))
