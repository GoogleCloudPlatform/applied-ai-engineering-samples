#!/bin/bash

# Determine the directory of the script.
if [ -n "$BASH_SOURCE" ]; then
  # Bash
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "$ZSH_VERSION" ]; then
  # Zsh
  SCRIPT_DIR="$(cd "$(dirname "${(%):-%N}")" && pwd)"
else
  # Fallback for other shells
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

# Set environment variables by sourcing the set_variables script.
echo "Setting environment variables..."
echo ""
source "$SCRIPT_DIR/set_variables.sh"

# Get the extractions dataset folder name from user input.
echo "Enter the name of the folder in the staging bucket containing"
echo "the extractions to import to the Agent Builder Data Store."
echo "It will be located under the 'source-data' top-level folder."
echo ""
echo "dataset_name: "
read dataset_name
echo ""

# Execute the workflow.
gcloud workflows execute t2x-doc-ingestion-workflow --project=$PROJECT --location=$REGION --data="{\"dataset_name\":\"$dataset_name\"}" --impersonate-service-account=$TF_VAR_terraform_service_account
