# Saxml on Google Kubernetes Engine 

This reference guide compiles prescriptive guidance for deploying and operating the [Saxml inference system](https://github.com/google/saxml) on [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine). It also provides comprehensive examples of serving and performance testing of large Generative AI models, such as the Llama2 series.

## High level architecture  

The diagram below illustrates the high-level architecture of the Saxml system on Google Kubernetes Engine.


![arch](images/saxml-gke.png)

- The foundation of the environment is a standard, regional, VPC-native GKE cluster with two types of node pools: TPU v5e node pools and CPU node pools
- TPU node pools host Saxml Model Servers
- A dedicated fixed size CPU node pool hosts Saxml Admin Servers. 
- A dedicated autoscaling CPU node pool hosts Saxml HTTP Proxy instances 
- Another dedicated autoscaling CPU node pool is used to deploy auxilliary workloads like checkpoint converter jobs and load generation tooling. 
- GKE nodes are configured to a use a custom service account
- The cluster is configured to support Workload Identity.
- Cloud Logging and Cloud Monitoring are used for logs and metrics management
- Custom docker images are managed Artifact Registry
- If deployed, Load generation tooling  is integrated with **Pubsub** and **Big Query** for load testing metrics tracking and analysis

 

## Environment setup
The deployment process is divided into 3 stages:

1. Base Environment: In this stage, the core infrastructure components are configured, including a VPC, a GKE cluster, service accounts, and storage buckets. The deployment process allows for the use of existing VPCs and/or service accounts to align with common IT governance structures in enterprises.

2. Performance Testing Environment: This is an optional phase where GCP services required to support load generation and performance metrics tracking are configured, including Pubsub and BigQuery.

3. Saxml Deployment: In this stage, Saxml servers and utilities are deployed to the GKE cluster.

You can execute each stage separately, or perform a one-click deployment of all components using the provided Cloud Build configuration.

To run the setup and execute code samples, you will need a workstation with [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk), [Terraform](https://www.terraform.io/), [Kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize), [Skaffold](https://skaffold.dev), and [kubectl](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl) utilities. We recommend using [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell), which has all the utilities pre-installed.


### Pre-requisites

Before proceeding with the deployment stages, you must:

- Create a new Google Cloud project or select an existing one.
- Enable the necessary services.
- Configure an automation service account and an automation Google Cloud storage bucket.


The following services are required by the base environment:
- `cloudbuild.googleapis.com`
- `artifactregistry.googleapis.com`
- `cloudkms.googleapis.com`
- `cloudresourcemanager.googleapis.com`
- `container.googleapis.com`
- `compute.googleapis.com`
- `container.googleapis.com`
- `iam.googleapis.com`
- `iamcredentials.googleapis.com`
- `serviceusage.googleapis.com`
- `stackdriver.googleapis.com`
- `storage-component.googleapis.com`
- `storage.googleapis.com`
- `sts.googleapis.com`

The following additional services are required if you deploy the performance testing components:
- `bigquery.googleapis.com`
- `pubsub.googleapis.com`

You also need a GCS bucket that will be used for managing Terraform state and other Terraform artifacts and a service account that will be impersonated by Terraform when provisioning the environment. The service account should have the following project level roles:
- `iam.securityAdmin`
- `iam.serviceAccountAdmin`
- `compute.networkAdmin`
- `container.admin`
- `iam.serviceAccountUser`
- `storage.admin`
- `artifactregistry.admin`

If the performance testing components are being deployed additional roles are required:
- `pubsub.editor`
- `bigquery.admin`

#### Configuring the prerequisites using the bootstrap Terraform 

The prerequisites may need to be configured by your GCP organization administrator. If you have access to a project where you are a project owner, you can configure the prerequisites using the Terraform configuration in the `environment/0-bootstrap` folder.

1. Clone this repo
2. Change the current folder to `ai-infrastructureenvironment/saxml-on-gke/environment/0-bootstrap`
3. Copy the `terraform.tfvars.tmpl` file to `terraform.tfvars`
4. Modify the `terraform.tfvars` file to reflect your environment
  - Set `project_id` to your project ID
  - Set `automation_bucket` to the name of a bucket you want to create in your project
  - Set `location` to your location
  - Set `automation_sa_name` to the automation service account name in your environment
5. Execute the `terraform init` command
6. Execute the `terraform apply` command

Besides enabling the necessary services and setting up an automation service account and an automation GCS bucket, the Terraform configuration has generated prepopulated template files for configuring the Terraform backend and providers, which can be utilized in the following setup stages. These template files are stored in the `gs://<YOUR-AUTOMATION-BUCKET/providers` folder.

#### Impersonating the automation service account

To be able to use the automation service account, the account that will be used to run Terraform commands needs to  have the `iam.serviceAccountTokenCreator` rights on the automation service account. You can grant this permission using the following command. Make sure to set the AUTOMATION_SERVICE_ACCOUNT and TERRAFORM_USER_ACCOUNT variables to the email addresses of the accounts in your environment.

```
AUTOMATION_SERVICE_ACCOUNT=you-automation-service-account-name@jk-mlops-dev.iam.gserviceaccount.com
TERRAFORM_USER_ACCOUNT=your-terraform-user@foo.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="user:$TERRAFORM_USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```

### One-click deployment

TBD

### Step by step deployment 

As an alternative to a one-click deployment, you can run each stage of the setup individually.

#### Provisioning the base environment

The Terraform configuration in the `environment/1-base_environment` folder creates and configures all the necessary components for deploying and serving Saxml models, including a VPC, a GKE cluster, service accounts, CPU and TPU node pools, and storage buckets.

##### Configure the Terraform providers and state

If you used the `bootstrap` configuration to configure the prerequisites, copy the `providers\providers.tf` and `providers\backend.tf` files from the `providers` folder in your automation bucket to the `1-base_environment` folder in the cloned repo. Modify the `backend.tf` by setting the `prefix` field to the name of a folder in the automation bucket where you want to store your Terraform configuration's state. For example, if you want to manage the Terraform state in the `tf_state/saxml` subfolder of the automation bucket set the `prefix` field to `tf_state/saxml`.

If the automation bucket and the automation service account were provided to you by your administrator, rename the `backend.tf.tmpl` and the `providers.tf.tmpl` files to `backend.tf` and `providers.tf` and update them with your settings.

##### Configure Terraform variables

You need to set the input variables required by the Terraform configuration to reflect your environment. Rename the `terraform.tfvars.tmpl` file to `terraform.tfvars` and update the settings.

*TBD. The detailed instruction to follow. For now refer to the variables.tf for more information on the configurable settings.*

##### Apply the configuration

```
terraform init
terraform apply
```

#### Provisioning performance testing components

This stage is optional. If you plan to conduct performance tests using the process and tools described in the [Examples](/ai-infrastructure/saxml-on-gke/examples/README.md) section of this repository, you must configure the Pubsub and BigQuery services required for load generation and metrics tracking tooling

The Terraform configuration for the performance testing environment is in the `environment/2-load_generation` folder.

##### Configure the Terraform providers and state

Follow the process outlined in the previous section to configure the `backend.tf` and `providers.tf` files.

##### Configure Terraform variables

Rename the `terraform.tfvars.tmpl`` file to `terraform.tfvars`` and update it to match your environment settings.

*TBD. The detailed instruction to follow. For now refer to the variables.tf for more information on the configurable settings.*

##### Apply the configuration

```
terraform init
terraform apply
```

#### Provisioning Saxml inference system

After the base infrastructure has been provisioned you can deploy Saxml components to your GKE cluster. The deployment process has been automated with **Skaffold** and **Kustomize**. You can find the Kustomize configuration in the `environment/3-saxml/manifests` folder. To deploy Saxml:
1. Update the `kustomization.yaml` with the namespace created during the base environment setup. This namespace will be used to deploy Saxml components. 

```
cd environment/3-saxml/manifests
NAMESPACE="your-namespace"
kustomize edit set namespace $NAMESPACE
```

2. Update the `kustomization.yaml` with the URI of the Saxml HTTP Proxy image. The image name should be `saxml-proxy`. The registry URI component of the image URI should be set to your  Artifact Registry.
```
PROJECT_ID="your-project-id"
DEFAULT_REPO="gcr.io/$PROJECT_ID"
SAXML_PROXY_IMAGE_URI="$DEFAULT_REPO/saxml-proxy:latest"
kustomize edit set image saxml-proxy=$SAXML_PROXY_IMAGE_URI

```
3. Update the `parameters.env` to reflect your desired configuration

*More details to follow*

4. Deploy the Saxml components:

```
cd environment/3-saxml
skaffold run --default-repo $DEFAULT_REPO 
```

*TBD. The detailed instructions for  Saxml configuration and monitoring to follow.* 

### Deploying Saxml models

This repository contains comprehensive examples for deploying and performance testing various Generative AI models, including Llama2, 7B, 13B, and 70B. For detailed instructions, please refer to the [Examples section](/ai-infrastructure/saxml-on-gke/examples/README.md) of the repository.

### Destroying the environment

#### Load generation

From the `3-load_generato` folder.

```
terraform destroy
```

#### Base environment

From the `1-base_environment` folder.

```
terraform destroy
```

[!WARNING] 
Sporadically, the `terrafom destroy` may fail on the removing the Kubernetes namespace step. To mitigate it, manually remove the namespace from the Terrafrom state and repeat the `terraform destroy`. 

Show the state:
```
terraform state list
```

Remove the state:

```
terraform state rm kubernetes_namespace.namespace
```


#### Bootstrap

If you provisioned the prerequistes using the bootstrap configuration you can optionally remove the automation account and the automation bucket.

From the `0-bootstrap` folder:

```
terraform destroy
```




