# Automation bootstrap

This Terraform module establishes the initial configuration of a GCP project that requires elevated administrative permissions. Its primary objective is to set up Terraform and Cloud Build automation for subsequent provisioning tasks. The module enables the specified set of services and sets up an automation service account along with an automation GCS bucket. Optionally, the module can create a GCP project.

## Examples 

```
module "automation_bootstrap" {
  source              = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/bootstrap"
  project_id          = "project-id" 
  automation_bucket   = {
    name =     "automation-bucket-name"
    location = "us-central1"
  automation_sa_name  = "service-account-name"
  services            = [
    "aiplatform.googleapis.com"
  ]
  roles               = [
    "roles/aiplatform.user"
  ]
}
```

By default the module enables the following  services:

- accesscontextmanager.googleapis.com
- artifactregistry.googleapis.com
- cloudbuild.googleapis.com
- cloudkms.googleapis.com
- cloudresourcemanager.googleapis.com
- container.googleapis.com
- compute.googleapis.com
- container.googleapis.com
- iam.googleapis.com
- iamcredentials.googleapis.com
- serviceusage.googleapis.com
- sourcerepo.googleapis.com
- stackdriver.googleapis.com
- storage-component.googleapis.com
- storage.googleapis.com
- sts.googleapis.com

You can specify additional services to enable through the services input variable.

By default, the following roles are assigned to the automation service account:

- roles/iam.securityAdmin
- roles/iam.serviceAccountAdmin
- roles/compute.networkAdmin
- roles/container.admin
- roles/iam.serviceAccountUser
- roles/storage.admin
- roles/artifactregistry.admin

You can specify additional roles to assign to the automation service account through the roles input variable.


## Impersonating automation service account

To be able to use the automation service account, the account that will be used to run Terraform commands in the other deployment stages needs to  have the `iam.serviceAccountTokenCreator` rights on the automation service account. You can grant this permission using the following command. Make sure to set the AUTOMATION_SERVICE_ACCOUNT and TERRAFORM_USER_ACCOUNT variables to the email addresses of the accounts in your environment.


```
AUTOMATION_SERVICE_ACCOUNT=you-automation-service-account-name@jk-mlops-dev.iam.gserviceaccount.com
TERRAFORM_USER_ACCOUNT=your-terraform-user@foo.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="user:$TERRAFORM_USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```

If the impersonating account itself is a service account, such as the Cloud Build service account:


```
AUTOMATION_SERVICE_ACCOUNT=you-automation-service-account-name@jk-mlops-dev.iam.gserviceaccount.com
TERRAFORM_USER_ACCOUNT=your-terraform-user@foo.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="serviceAccount:$TERRAFORM_USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```


## Input variables

| Name | Description | Type | Required | Default |
|---|---|---|---|---|
|[project_id](variables.tf#L31)| The project ID, where to enable services and create an automation service account and an automation bucket|`string`| &check; ||
|[deletion_protection](variables.tf#L28)|Prevent Terraform from destroying the automation bucket. When this field is set, a terraform destroy or terraform apply that would delete the bucket will fail.|`string`||`true`|
|[automation_bucket](variables.tf#L22)| Settings for the automation bucket |`map(strings)`|&check;||
|[automation_sa_name](variables.tf#L37)|The name of the automation service account|`string`| &check;||
|[services](variables.tf#L43)|The list of additional services to enable|`list(strings)`| &check; ||
|[roles](varialbes.tf#L50)|The list of additional roles to assign to the automation service account|`list(strings)`|&check; ||


## Outputs

| Name | Description | 
|---|---|
|[automation_sa](outputs.tf#L42)|The email of the automation service account|
|[automation_gcs](outputs.tf#L37)|The name of the automation bucket|



The module also creates two files in the `gs://<AUTOMATION_BUCKET_NAME>/providers`

- the `providers.tf` file

```
provider "google" {
  impersonate_service_account = "automation-sa-name@project-id.iam.gserviceaccount.com"
}
provider "google-beta" {
  impersonate_service_account = "automation-sa-name@project-id.iam.gserviceaccount.com"
}
```

- the `backend.tf` file

```
terraform {
  backend "gcs" {
    bucket                      = "automation-bucket-name"
    impersonate_service_account = "automation-sa-name@project-id.iam.gserviceaccount.com"
    # remove the newline between quotes and set the prefix to the folder for Terraform state
    prefix = "
    "
  }
}
```

You can utilize these files in the downstream Terraform stages to configure the management of Terraform state in Cloud Storage and enable Terraform impersonation.





