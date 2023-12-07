#!/bin/bash
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Setting variables using vars.env 
export REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
pushd ${REPO_ROOT_DIR}/env_setup
source vars.env

[[ ! "${PROJECT_ID}" ]] && echo -e "Please export PROJECT_ID variable (\e[95mexport PROJECT_ID=<YOUR PROJECT ID>\e[0m)\nExiting." && exit 0
echo -e "\e[95mPROJECT_ID is set to ${PROJECT_ID}\e[0m"

gcloud config set core/project ${PROJECT_ID} && \

gcloud builds submit \
  --config cloudbuild.destroy.yaml \
  --substitutions _TF_STATE_BUCKET=$TF_STATE_BUCKET,_TF_STATE_PREFIX=$TF_STATE_PREFIX,_REGION=$REGION,_TENSORBOARD_REGION=$TENSORBOARD_REGION,_ZONE=$ZONE,_ARTIFACT_REPOSITORY_BUCKET_NAME=$ARTIFACT_REPOSITORY_BUCKET_NAME,_NETWORK_NAME=$NETWORK_NAME,_SUBNET_NAME=$SUBNET_NAME,_CLUSTER_NAME=$CLUSTER_NAME,_NAMESPACE=$NAMESPACE,_TPU_TYPE=$TPU_TYPE,_NUM_TPU_POOLS=$NUM_TPU_POOLS \
  --timeout "2h" \
  --machine-type=e2-highcpu-32 \
  --quiet \
  --async && \

echo -e "\e[95mYou can view the Cloudbuild status through https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}\e[0m"