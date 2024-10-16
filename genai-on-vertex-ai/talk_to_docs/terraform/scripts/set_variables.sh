#!/bin/bash

# The user completes these prerequisite commmands (Google Cloud Shell sets them up automatically):
# gcloud auth login
# gcloud config set project 'my-project-id' # replace 'my-project-id' with your project ID
# [OPTIONAL] gcloud config set compute/region us-central1

# Set the PROJECT variable.
export PROJECT=$(gcloud config list --format='value(core.project)')

# Get the default compute region from gcloud.
region=$(gcloud config list --format='value(compute.region)')

# Set the REGION variable and the default gcloud compute.region attribute to us-central1 if it is unset.
if [ -z "$region" ]; then
  export REGION="us-central1"
  gcloud config set compute/region $REGION

# Use the default gcloud compute.region attribute if it is set.
else
  export REGION=$region
fi

# Set the project_id and terraform_service_account Terraform input variables.
export TF_VAR_project_id=$PROJECT
export TF_VAR_terraform_service_account="terraform-service-account@${PROJECT}.iam.gserviceaccount.com"

# Set the REPO_ROOT environment variable.
export REPO_ROOT=$(git rev-parse --show-toplevel)

# Display the environment variables.
echo ""
echo "PROJECT: $PROJECT"
echo "REGION: $REGION"
echo "TF_VAR_project_id: $TF_VAR_project_id"
echo "TF_VAR_terraform_service_account: $TF_VAR_terraform_service_account"
echo "REPO_ROOT: $REPO_ROOT"
echo ""
