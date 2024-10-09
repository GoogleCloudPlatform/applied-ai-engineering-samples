#!/bin/bash
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Make sure following env variables a re properly set:
#
# 1. AUDIENCE using IP/domain of the T2X Endpoint:
# export AUDIENCE='https://34.54.24.62.nip.io/t2x-api'
#
# 2. Cloud run invoker service account:
# export RUN_INVOKER_SERVICE_ACCOUNT="run-invoker-service-account@${PROJECT}.iam.gserviceaccount.com"

TOKEN=$(
  gcloud auth print-identity-token \
  --impersonate-service-account="$RUN_INVOKER_SERVICE_ACCOUNT" \
  --audiences="$AUDIENCE"
)

curl -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
        "question": "I injured my back. Is massage therapy covered?",
        "member_context_full": {
          "set_number": "001acis",
          "member_id": "1234"
        }
      }' \
  "${AUDIENCE}"/respond/


# Sample Answer:
#{
#  "round_number": "1",
#  "answer": "Massage therapy is covered under the chiropractic benefit if it is part of the chiropractor's overall treatment plan. The member's plan will determine the specific coverage details, such as the deductible, copay, and coinsurance amounts. For more information, please refer to the member's specific benefit plan document. The member may also want to contact their provider to discuss their specific coverage and treatment plan.",
#  "response_id": "",
#  "plan_and_summaries": "",
#  "additional_information_to_retrieve": "",
#  "context_used": [
#    "therapy - msk pain management benefit (lower back program)",
#    "mahp plan-specific coverages"
#  ],
#  "urls_to_kc": [
#    "https://kmead.uhc.com/km-content-service/default/content/vkm%3AAuthoredContent/LEwGOb1FxM5FevNasiCwz8/en-US?version=3.0",
#    "https://kmead.uhc.com/km-content-service/default/content/vkm%3AAuthoredContent/Sa5K6iOpNV8bzJRnqrndf9/en-US?version=2.0"
#  ],
#  "attributes_to_kc_km": [
#    {
#      "doc_type": "km",
#      "doc_identifier": "km1738060",
#      "url": "https://kmead.uhc.com/km-content-service/default/content/vkm%3AAuthoredContent/Sa5K6iOpNV8bzJRnqrndf9/en-US?version=2.0",
#      "section_name": "therapy - msk pain management benefit (lower back program)"
#    },
#    {
#      "doc_type": "km",
#      "doc_identifier": "km1737854",
#      "url": "https://kmead.uhc.com/km-content-service/default/content/vkm%3AAuthoredContent/LEwGOb1FxM5FevNasiCwz8/en-US?version=3.0",
#      "section_name": "mahp plan-specific coverages"
#    }
#  ],
#  "attributes_to_kc_mp": [],
#  "attributes_to_b360": [],
#  "confidence_score": "95",
#  "session_id": "1f0524ef-fd92-4c66-bf92-2aa9b7ee41cc"
#}


