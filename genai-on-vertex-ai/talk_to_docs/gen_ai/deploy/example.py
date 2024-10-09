# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This module provides an example on how to call Talk2Docs API. 
It uses fake data as member_context_full

You can run it either in the localhost mode (when T2X end point is running locally), or can access remote Server.


For the Remote Server you will need to set following env variables:

API_DOMAIN                - Talk2Docs Endpoint, for example: x.241.x.173.nip.io
DEVELOPER_SERVICE_ACCOUNT - Service account used for impersonation and token retrieval.
                            Must have roles/iam.serviceAccountTokenCreator and roles/run.invoker

In cloud shell:

export PROJECT_ID=...
export API_DOMAIN=...

export DEVELOPER_SERVICE_ACCOUNT_NAME="t2d-developer"
export DEVELOPER_SERVICE_ACCOUNT="$DEVELOPER_SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create $DEVELOPER_SERVICE_ACCOUNT \
  --display-name $DEVELOPER_SERVICE_ACCOUNT \
  --project $PROJECT_ID

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:$DEVELOPER_SERVICE_ACCOUNT" \
  --role "roles/run.invoker" \
  --role "roles/iam.serviceAccountTokenCreator"

python example.py

"""
import os

import requests
import google
import google.auth
from google.auth import impersonated_credentials
import google.auth.transport.requests
import google.oauth2.credentials

api_domain = os.environ.get("API_DOMAIN")
example_target_principal = os.environ.get("DEVELOPER_SERVICE_ACCOUNT")

if api_domain:
    example_audience = f"https://{api_domain}/t2x-api"
else:
    example_audience = "http://127.0.0.1:8080"

example_target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]


def get_impersonated_id_token(target_principal: str, target_scopes: list, audience: str | None = None) -> str:
    """Use Service Account Impersonation to generate a token for authorized requests.
    Caller must have the “Service Account Token Creator” role on the target service account.
    Args:
        target_principal: The Service Account email address to impersonate.
        target_scopes: List of auth scopes for the Service Account.
        audience: the URI of the Google Cloud resource to access with impersonation.
    Returns: Open ID Connect ID Token-based service account credentials bearer token
    that can be used in HTTP headers to make authenticated requests.
    refs:
    https://cloud.google.com/docs/authentication/get-id-token#impersonation
    https://cloud.google.com/iam/docs/create-short-lived-credentials-direct#user-credentials_1
    https://stackoverflow.com/questions/74411491/python-equivalent-for-gcloud-auth-print-identity-token-command
    https://googleapis.dev/python/google-auth/latest/reference/google.auth.impersonated_credentials.html
    The get_impersonated_id_token method is equivalent to the following gcloud commands:
    https://cloud.google.com/run/docs/configuring/custom-audiences#verifying
    """
    # Get ADC for the caller (a Google user account).
    creds, _ = google.auth.default()

    # Create impersonated credentials.
    target_creds = impersonated_credentials.Credentials(
        source_credentials=creds,
        target_principal=target_principal,
        target_scopes=target_scopes
    )

    # Use impersonated creds to fetch and refresh an access token.
    request = google.auth.transport.requests.Request()
    id_creds = impersonated_credentials.IDTokenCredentials(
        target_credentials=target_creds,
        target_audience=audience,
        include_email=True
    )
    id_creds.refresh(request)

    return id_creds.token


def get_token(audience: str):
    if not api_domain: return None
    return get_impersonated_id_token(
        target_principal=example_target_principal,
        target_scopes=example_target_scopes,
        audience=audience,
    )


def main():
    """This is main function that serves as an example how to use the respond API method"""
    url = f"{example_audience}/respond/"

    data = {
        "question": "I injured my back. Is massage therapy covered?",
        "member_context_full": {"set_number": "001acis", "member_id": "1234"},
    }

    token = get_token(example_audience)
    if token:
        response = requests.post(url, json=data, headers={"Authorization": f"Bearer {token}"}, timeout=3600)
    else:
        response = requests.post(url,  json=data, timeout=3600)

    if response.status_code == 200:
        print("Success!")
        print(response.json())  # This will print the response data
    else:
        print("Error:", response.status_code)
        print(response.text)  # This will print the error message, if any


if __name__ == "__main__":
    main()
