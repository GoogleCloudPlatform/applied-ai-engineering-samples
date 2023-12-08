# Automation bootstrap

This Terraform module establishes the initial configuration of a GCP project that requires elevated administrative permissions. Its primary objective is to set up Terraform and Cloud Build automation for subsequent provisioning tasks. The module enables the specified set of services and sets up an automation service account along with an automation GCS bucket. Optionally, the module can create a GCP project.

## Usage

TBD.

## Impersonating automation service account

To be able to use the automation service account, the account that will be used to run Terraform commands in the other deployment stages needs to  have the `iam.serviceAccountTokenCreator` rights on the automation service account. You can grant this permission using the following command. Make sure to set the AUTOMATION_SERVICE_ACCOUNT and TERRAFORM_USER_ACCOUNT variables to the email addresses of the accounts in your environment.

```
AUTOMATION_SERVICE_ACCOUNT=you-automation-service-account-name@jk-mlops-dev.iam.gserviceaccount.com
TERRAFORM_USER_ACCOUNT=your-terraform-user@foo.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="user:$TERRAFORM_USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```

