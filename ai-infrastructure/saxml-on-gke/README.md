# Saxml on Google Kubernetes Engine 

This reference guide compiles prescriptive guidance for deploying and operating the [Saxml inference system](https://github.com/google/saxml) on [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine). It also provides comprehensive examples of serving large Generative AI models, such as the Llama2 series, on Google Cloud TPUs.

## High level architecture  

The diagram below illustrates the high-level architecture of the Saxml system on Google Kubernetes Engine.

![arch](/images/saxml-gke.png)


## Environment setup
### Prerequisites

Provisioning of the Saxml system has been automated with Terraform. Before executing the Terraform configurations, you need to:

- Create or select an existing Google Cloud project.
- Enable the required services.
- Configure an automation service account and a Google Cloud storage bucket.

If you are the project owner, you can utilize the Terraform scripts in the `bootstrap` folder to enable the necessary services, as well as to create the automation service account and the automation storage bucket. Refer to the *Configuring the prerequisites using the bootstrap Terraform* section for instructions on how to use the bootstrat Terraform configuration.

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

You also need a GCS bucket that will be used for managing Terraform state and other Terraform artifacts and a service account that will be imporsonated by Terraform when provisioning the environment. The service account should have the following project level roles:

- `iam.securityAdmin`
- `iam.serviceAccountAdmin`
- `compute.networkAdmin`
- `container.admin`
- `iam.serviceAccountUser`
- `storage.admin`
- `pubsub.editor`
- `bigquery.admin`

#### Configuring the prerequisites using the bootstrap Terraform 

From [Cloud Shell](https://cloud.google.com/shell):
- Clone this repo
- Change the current folder to `environment/infrastructure/bootstrap`
- Copy the `terraform.tfvars.tmpl` file to `terraform.tfvars`
- Modify the `terraform.tfvars` file to reflect your environment
  - Set `project_id` to your project ID
  - Set `automation_bucket` to the name of a bucket you want to create in your project
  - Set `location` to your location
  - Set `automation_sa_name` to the automation service account name in your environment
- Execute the `terraform init` command
- Execute the `terraform apply` command


#### Impersonating the automation service account

To be able to use the automation service account, the account that will be used to run Terraform commands needs to  have the `iam.serviceAccountTokenCreator` rights on the automation service account. You can grant this permission using the following command. Make sure to set the AUTOMATION_SERVICE_ACCOUNT and TERRAFORM_USER_ACCOUNT variables to the email addresses of the accounts in your environment.

```
AUTOMATION_SERVICE_ACCOUNT=you-automation-service-account-name@jk-mlops-dev.iam.gserviceaccount.com
TERRAFORM_USER_ACCOUNT=your-terraform-user@foo.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="user:$TERRAFORM_USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```

### Provisionining the Saxml system

Once the automation service account and the automation bucket are configured, you can utilize Terraform to provision the Saxml system.

The provisioning of the Saxml system consists of two steps:

1. Provisioning the base system, which includes all the components necessary to deploy and serve Saxml models.
2. Optionally, provisioning a load generation and performance tracking components.


#### Provisionning the base system

The Terraform configuration in the `base_environment` folder creates and configures all the necessary components for deploying and serving Saxml models, including a VPC, a GKE cluster, service accounts, CPU and TPU node pools, and storage buckets.

##### Configure providers and state

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

#### Provisioning the load generation components

TBD


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

Copy the identifier of the namespace state. E.g. ``

Remove the state:

```
terraform state rm lll``
```


#### Bootstrap

If you provisioned the prerequistes using the bootstrap configuration you can optionally remove the automation account and the automation bucket.

From the `bootstrap` folder:

```
terraform destroy
```


## Deploying Saxml  

TBD



