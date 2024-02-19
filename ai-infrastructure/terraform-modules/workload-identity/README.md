# Workload Identity Configuration

This Terraform module configures [workload identity federation for Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity). The module offers the flexibility to utilize an existing IAM service account, Kubernetes service account, and Kubernetes namespace, or create new ones as needed.

## Examples 

```
module "wid" {
  source       = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/workload-identity"
  cluster_name = "gke-cluster" 
  location     = "us-central1"
  project_id   = "project-id"
  wid_sa_name  = "iam-wid-sa"
  wid_sa_roles = ["storage.objectAdmin", "logging.logWriter"]]
  ksa_name     = "wid-ksa"
  namespace    = "wid-namespace"
  
}
```



## Input variables

| Name | Description | Type | Required | Default |
|---|---|---|---|---|
|[project_id](variables.tf#L31)| The project ID|`string`| &check; ||
|[cluster_name](variables.tf#16) | The name of a GKE cluster |`string`| &check;||
|[location](variables.tf#L22)| The location of a GKE cluster |`string`|&check;||
|[namespace](variables.tf#L34)|The name of a Kubernetes namespace |`string`| &check;||
|[namespace_create](variables.tf#L40)|Whether to create a new namspace |`bool`| |`true`|
|[ksa_name](variables.tf#L46)|The name of a Kubernetes service account |`string`| &check; ||
|[kubernetes_service_account_create](variables.tf#L52)|Whether to create a new Kubernetes service account |`bool`| |`true`|
|[wid_sa_name](variables.tf#L58)|The name of an IAM service account |`string`| &check; ||
|[wid_sa_roles](varialbes.tf#L70)|The list of IAM roles to assign to the IAM service account|`list(strings)`|&check; ||
|[google_service_account_create](variables.tf#L64)|Whether to create a new IAM service account |`bool`| |`true`|


## Outputs

| Name | Description | 
|---|---|
|[wid_sa_email](outputs.tf#L31)|The email of the IAM  service account|
|[wid_sa_name](outputs.tf#L36)|The name of the IAM service account|
|[namespace](outputs.tf#L41)|The name of the Kubernetes namespace|
|[ksa_name](outputs.tf#L36)|The name of the Kubernetes service account|
|[created_resources](outputs.tf#L15)|The IDs of newly created resources|



