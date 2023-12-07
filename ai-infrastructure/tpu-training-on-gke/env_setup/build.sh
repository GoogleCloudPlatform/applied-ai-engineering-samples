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

[[ ! "${PROJECT_ID}" ]] && echo -e "Please export PROJECT_ID variable (\e[95mexport PROJECT_ID=<YOUR_PROJECT_ID>\e[0m)\nExiting." && exit 0
echo -e "\e[95mPROJECT_ID is set to ${PROJECT_ID}\e[0m"

# Enable APIs

gcloud config set core/project ${PROJECT_ID} && \
export PROJECT_NUM=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)') && \
export TF_CLOUDBUILD_SA="${PROJECT_NUM}@cloudbuild.gserviceaccount.com" && \
echo -e "$TF_CLOUDBUILD_SA" && \
echo -e "\e[95mEnabling required APIs in ${PROJECT_ID}\e[0m" && \
gcloud --project="${PROJECT_ID}" services enable \
cloudbuild.googleapis.com \
compute.googleapis.com \
cloudresourcemanager.googleapis.com \
iam.googleapis.com \
container.googleapis.com \
cloudtrace.googleapis.com \
iamcredentials.googleapis.com \
monitoring.googleapis.com \
logging.googleapis.com \
aiplatform.googleapis.com \
config.googleapis.com && \

# Assign permissions to Cloud Build Service Account
echo -e "\e[95mAssigning Cloudbuild Service Account roles/owner in ${PROJECT_ID}\e[0m" && \
# gcloud projects add-iam-policy-binding "${PROJECT_ID}" --member serviceAccount:"${TF_CLOUDBUILD_SA}" --role roles/owner --condition None && \

echo -e "\e[95mCreating Google Cloud Cloudbuild to create infrastructure...\e[0m" && \

[[ $(gcloud artifacts repositories list --location=$REGION --format="value(name)" | grep ${ARTIFACT_REGISTRY_NAME}) ]] || \
gcloud artifacts repositories create ${ARTIFACT_REGISTRY_NAME} --repository-format=docker --location=$REGION --description="Repo for platform installer container images built by Cloud Build." && \

echo -e "\e[95mStarting Cloudbuild to create infrastructure...\e[0m" && \

gcloud builds submit \
  --config cloudbuild.provision.yaml \
  --substitutions _TF_STATE_BUCKET=$TF_STATE_BUCKET,_TF_STATE_PREFIX=$TF_STATE_PREFIX,_REGION=$REGION,_TENSORBOARD_REGION=$TENSORBOARD_REGION,_ZONE=$ZONE,_ARTIFACT_REPOSITORY_BUCKET_NAME=$ARTIFACT_REPOSITORY_BUCKET_NAME,_NETWORK_NAME=$NETWORK_NAME,_SUBNET_NAME=$SUBNET_NAME,_CLUSTER_NAME=$CLUSTER_NAME,_NAMESPACE=$NAMESPACE,_TPU_TYPE=$TPU_TYPE,_NUM_TPU_POOLS=$NUM_TPU_POOLS,_NUM_OF_CHIPS=$NUM_OF_CHIPS,_JOBSET_API_VERSION=$JOBSET_API_VERSION,_KUEUE_API_VERSION=$KUEUE_API_VERSION \
  --timeout "2h" \
  --machine-type=e2-highcpu-32 \
  --quiet \
  --async && \

echo -e "\e[95mYou can view the Cloudbuild status through https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}\e[0m"