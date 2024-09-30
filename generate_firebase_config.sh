#!/bin/bash
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


# Load environment variables
source env.vars

# Generate firebase_config.json
cat <<EOF > ./terraform/firebase_config.json
{
    "backend": {
      "prompt_template": "Answer the question based only on the following context:\\n{context}\\n\\nQuestion:\\n{query}\\n\\nAnswer:\\n"
    },
    "gcp_project": {
      "project_id": "$PROJECT_ID",
      "location": "$REGION"
    },
    "vertex": {
      "project_id": "$PROJECT_ID",
      "region": "$REGION"
    },
    "cloud_workflows": {
      "project_id": "$PROJECT_ID",
      "location": "$REGION",
      "workflow_name": "$WORKFLOW_NAME"
    },
    "pubsub": {
      "project_id": "$PROJECT_ID",
      "topic_id": "$INPUT_TOPIC_NAME"
    }
}
EOF