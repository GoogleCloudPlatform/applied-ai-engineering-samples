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

# Usage:
# bash config_namespace.sh NAMESPACE=<namespace> KSA_NAME=<ksa_name> GSA_EMAIL=<gsa_email> ARTIFACT_REGISTRY_PATH=<artifact_registry_path>

set -e

usage() {
    echo -e "\n\nError: $1"
    echo "Usage: bash config_namespace.sh NAMESPACE=<namespace> KSA_NAME=<ksa_name> GSA_EMAIL=<gsa_email> ARTIFACT_REGISTRY_PATH=<artifact_registry_path>"
    exit 2
}

# Set environment variables
for ARGUMENT in "$@"; do
    IFS='=' read -r KEY VALUE <<< "$ARGUMENT"
    export "$KEY"="$VALUE"
done

# Validate parameters
if [[ -z $NAMESPACE ]]; then
    usage "NAMESPACE not set"
fi

if [[ -z $KSA_NAME ]]; then
    usage "KSA_NAME not set"
fi

if [[ -z $GSA_EMAIL ]]; then
    usage "GSA_EMAIL not set"
fi

if [[ -z $ARTIFACT_REGISTRY_PATH ]]; then
    usage "ARTIFACT_REGISTRY_PATH not set"
fi

echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml --save-config | kubectl apply -f -

echo "Creating service account: $KSA_NAME"
kubectl create serviceaccount $KSA_NAME -n $NAMESPACE --dry-run=client -o yaml --save-config | kubectl apply -f -

echo "Annotating the account for WID: iam.gke.io/gcp-service-account=$GSA_EMAIL"
kubectl annotate serviceaccount $KSA_NAME "iam.gke.io/gcp-service-account=$GSA_EMAIL" -n $NAMESPACE

