# Saxml on Google Kubernetes Engine 

This reference guide compiles prescriptive guidance for deploying and operating the [Saxml inference system](https://github.com/google/saxml) on [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine). It also provides comprehensive examples of serving large Generative AI models, such as the Llama2 series.

## High level architecture  

The diagram below illustrates the high-level architecture of the Saxml system on Google Kubernetes Engine.

*NOTE. Diagram and the architecture description to be updated*

![arch](images/saxml-gke.png)


## Environment setup
The deployment process has been automated using Terraform, Kustomize, and Cloud Build, and it is divided into four stages:

1. Bootstrap: During this stage, an automation service account and an automation storage bucket are created within the selected GCP project. The automation service account is configured with a limited set of permissions necessary for resource provisioning in subsequent stages and can be used by automation tools for impersonation. The automation bucket is used to manage Terraform state and other deployment artifacts. Project ownership is required to complete the bootstrap stage.

2. Base Environment: In this stage, the core infrastructure components are configured, including a VPC, a GKE cluster, service accounts, and storage buckets. The deployment process allows for the use of existing VPCs and/or service accounts to align with common IT governance structures in enterprises.

3. Performance Testing Environment: This is an optional phase where GCP services required to support load generation and performance metrics tracking are configured, including Pubsub and BigQuery.

4. Saxml Deployment: In this stage, Saxml servers and utilities are deployed to the GKE cluster.

You can execute each stage separately, or with the necessary permissions, perform a one-click deployment of all components using the provided Cloud Build configuration.

### Step by step deployment

This section offers step-by-step instructions for executing each stage

#### Bootstrap 

Before proceeding with other deployment stages, you must:

- Create a new Google Cloud project or select an existing one.
- Enable the necessary services.
- Configure an automation service account and a Google Cloud storage bucket.

If you are the project owner, you can utilize the Terraform scripts in the `environment/0-bootstrap` folder to enable the necessary services, as well as to create the automation service account and the automation storage bucket. Refer to the *Configuring the prerequisites using the bootstrap Terraform* section for instructions on how to use the bootstrat Terraform configuration.

If you are not the project owner request that the following services are enabled in your project:

- `accesscontextmanager.googleapis.com`
- `cloudbuild.googleapis.com`
- `cloudkms.googleapis.com`
- `cloudresourcemanager.googleapis.com`
- `container.googleapis.com`
- `compute.googleapis.com`
- `container.googleapis.com`
- `iam.googleapis.com`
- `iamcredentials.googleapis.com`
- `servicenetworking.googleapis.com`
- `serviceusage.googleapis.com`
- `sourcerepo.googleapis.com`
- `stackdriver.googleapis.com`
- `storage-component.googleapis.com`
- `storage.googleapis.com`
- `sts.googleapis.com`

You also need a GCS bucket that will be used for managing Terraform state and other Terraform artifacts and a service account that will be impersonated by Terraform when provisioning the environment. The service account should have the following project level roles:

- `iam.securityAdmin`
- `iam.serviceAccountAdmin`
- `compute.networkAdmin`
- `container.admin`
- `iam.serviceAccountUser`
- `storage.admin`
- `pubsub.editor`
- `bigquery.admin`

##### Configuring the prerequisites using the bootstrap Terraform 

From [Cloud Shell](https://cloud.google.com/shell):
- Clone this repo
- Change the current folder to `environment/0-bootstrap`
- Copy the `terraform.tfvars.tmpl` file to `terraform.tfvars`
- Modify the `terraform.tfvars` file to reflect your environment
  - Set `project_id` to your project ID
  - Set `automation_bucket` to the name of a bucket you want to create in your project
  - Set `location` to your location
  - Set `automation_sa_name` to the automation service account name in your environment
- Execute the `terraform init` command
- Execute the `terraform apply` command


##### Impersonating the automation service account

To be able to use the automation service account, the account that will be used to run Terraform commands in the other deployment stages needs to  have the `iam.serviceAccountTokenCreator` rights on the automation service account. You can grant this permission using the following command. Make sure to set the AUTOMATION_SERVICE_ACCOUNT and TERRAFORM_USER_ACCOUNT variables to the email addresses of the accounts in your environment.

```
AUTOMATION_SERVICE_ACCOUNT=you-automation-service-account-name@jk-mlops-dev.iam.gserviceaccount.com
TERRAFORM_USER_ACCOUNT=your-terraform-user@foo.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="user:$TERRAFORM_USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```

#### Base environment

Once the automation service account and the automation bucket are configured, you can utilize Terraform to provision the base environment.

The Terraform configuration in the `environment/1-base_environment` folder creates and configures all the necessary components for deploying and serving Saxml models, including a VPC, a GKE cluster, service accounts, CPU and TPU node pools, and storage buckets.

##### Configure the Terraform providers and state

If you used the `bootstrap` configuration to configure the prerequisites, copy the `providers\providers.tf` and `providers\backend.tf` files from the `providers` folder in your automation bucket to the `base_environment` folder in the cloned repo. Modify the `backend.tf` by setting the `prefix` field to the name of a folder in the automation bucket where you want to store your Terraform configuration's state. For example, if you want to manage the Terraform state in the `tf_state/saxml` subfolder of the automation bucket set the `prefix` field to `tf_state/saxml`.

If the automation bucket and the automation service account were provided to you by your administrator, rename the `backend.tf.tmpl` and the `providers.tf.tmpl` files to `backend.tf` and `providers.tf` and update them with your settings.

##### Configure variables

You need to set the input variables required by the Terraform configuration to reflect your environment. Rename the `terraform.tfvars.tmpl` file to `terraform.tfvars` and update the settings.

*TBD. The detailed instruction to follow. For now refer to the variables.tf for more information on the configurable settings.*

##### Apply the configuration

```
terraform init
terraform apply
```

#### Performance testing environment

This stage is optional. If you wish to conduct  performance tests using the process and tools described in the [Examples section](/ai-infrastructure/saxml-on-gke/examples/README.md) section of this repository, you need to configure the Pubsub and BigQuery services required by the load generation and metrics tracking tooling.

The Terraform configuration for the performance testing environment is in the `environment/2-load_generation` folder.

##### Configure the Terraform providers and state

Follow the process outlined in the previous section to configure the `backend.tf` and `providers.tf` files.

##### Configure varialbles

Rename the `terraform.tfvars.tmpl` file to `terraform.tfvars` make the necessary updates to align with your environment settings

*TBD. The detailed instruction to follow. For now refer to the variables.tf for more information on the configurable settings.*

##### Apply the configuration

```
terraform init
terraform apply
```

#### Saxml inference system

After the base infrastructure has been provisioned you can deploy Saxml components to your GKE cluster. The deployment process has been automated with **Skaffold** and **Kustomize**. You can find the Kustomize configuration in the `environment/3-saxml/manifests` folder. To deploy Saxml:
1. Update the `kustomization.yaml` with your namespace 

```
NAMESPACE="your-namespace"
kustomize edit set namespace $NAMESPACE
```

2. Update the `kustomization.yaml` with the URI of the `saxml-proxy` image
```
SAXML_PROXY_IMAGE_URI="gcr.io/your-project/your-image-name:tag"

kustomize edit set image saxml-proxy=$SAXML_PROXY_IMAGE_URI

```
3. Update the `parameters.env` to reflect your desired configuration

4. Deploy the Saxml components:

```
skaffold run
```

*TBD. The detailed instructions for  Saxml configuration and monitoring to follow.* 

### Deploying Saxml models

This repository contains comprehensive examples for deploying and performance testing various Generative AI models, including Llama2, 7B, 13B, and 70B. For detailed instructions, please refer to the [Examples section](/ai-infrastructure/saxml-on-gke/examples/README.md) of the repository.

### Destroying the environment

#### Load generation

From the `load_generation` folder.

```
terraform destroy
```

#### Base environment

From the `base_environment` folder.

```
terraform destroy
```

NOTE. Sporadically the `terrafom destroy` may fail on the removing the Kubernetes namespace step. To mitigate it, manually remove the namespace from the TF state and repeat the `terraform destory`. To remove the namespace from the state.

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

From the `bootstrap` folder:

```
terraform destroy
```


## Deploying Saxml  

TBD



