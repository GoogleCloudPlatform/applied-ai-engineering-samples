# Saxml on Google Kubernetes Engine 

This reference guide compiles prescriptive guidance for deploying and operating the [Saxml inference system](https://github.com/google/saxml) on [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine). It also provides comprehensive examples of serving and performance testing of large Generative AI models, such as the Llama2 series.

## High level architecture  

The diagram below illustrates the high-level architecture of the Saxml system on Google Kubernetes Engine.


![arch](images/saxml-gke.png)

- The foundation of the environment is a standard, regional, VPC-native GKE cluster with two types of node pools: TPU v4/v5e node pools and CPU node pools.
- TPU node pools host **Saxml Model Servers**.
- A dedicated fixed size CPU node pool hosts **Saxml Admin Servers**. 
- A dedicated autoscaling CPU node pool hosts **Saxml HTTP Proxy** instances. **Saxml HTTP Proxy** is a custom API server that encapsulates **Saxml Client API** and exposes it through REST interfaces.
- A couple of autoscaling CPU node pools are used to deploy auxiliary workloads like checkpoint converter jobs, load generation tooling, and saxutil CLI. These node pools have different node hardware configurations to support various workloads.
- GKE nodes are configured to a use a custom service account
- The cluster is configured to support [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity).
- [Cloud Logging](https://cloud.google.com/logging?hl=en) and [Cloud Monitoring](https://cloud.google.com/monitoring?hl=en) are used for logs and metrics management
- Custom docker images are managed in [Artifact Registry](https://cloud.google.com/artifact-registry)
- If deployed, Load generation tooling  is integrated with [Pubsub](https://cloud.google.com/pubsub?hl=en) and [Big Query](https://cloud.google.com/bigquery) for load testing metrics tracking and analysis

 

## Setup

The deployment process is divided into 2 stages:

1. Base infrastructure: In this stage, the core infrastructure components are configured, including a VPC, a GKE cluster, service accounts, and storage buckets. Optionally, Pubsub and BigQuery services can also be installed to support performance testing management. The deployment process provides the flexibility to use existing VPCs and service accounts, aligning with common IT governance structures in enterprises.

2. Saxml Deployment: In this stage, Saxml servers and utilities are deployed to the GKE cluster.

The deployment process is automated using [Cloud Build](https://cloud.google.com/build), [Terraform](https://cloud.google.com/docs/terraform),  [Kustomize](https://kustomize.io/), and [Skaffold](ihttps://skaffold.dev/). 
To run the setup and execute code samples, you will need a workstation with [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk), [Terraform](https://www.terraform.io/), [Kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize), [Skaffold](https://skaffold.dev), and [kubectl](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl) utilities. We recommend using [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell), which has all the utilities pre-installed.



The first stage is automated with **Cloud Build** and **Terraform**. The **Cloud Build** configuration orchestrates the following steps:

- [ ] Creates a network, a subnet, and IP ranges for GKE pods and services.
- [ ] Creates a VPC-native cluster.
- [ ] Creates CPU node pools.
- [ ] Creates TPU node pools.
- [ ] Creates an IAM service account for Workload Identity and an IAM service account to be used as a custom node pool service account.
- [ ] Configures the cluster for Workload Identity.
- [ ] Creates a Kubernetes namespace to host Saxml servers and a Kubernetes service account to use with Workload Identity
- [ ] Creates two Google Cloud Storage buckets.
- [ ] Creates an Artifact Registry
- [ ] Creates a BigQuery dataset and table 
- [ ] Creates a Pubsub topic and BigQuery subscription

The last three steps are optional. They can be skipped by setting the `create_artifact_registry` and the `create_perf_testing_infrastructure` Terraform input variables to `false`.

The Terraform configuration creates and configures a new VPC  by default. However, you can also opt to use an existing VPC for a GKE cluster, as this functionality is supported by the [gke-aiml Terraform module](../terraform-modules/gke-aiml/README.md), which is used by the Terraform configuration.

To use an existing VPC you need to modify the inputs to the `module "base_environment"` in the `environment/1-base-infrastrucutre/main.tf` file, following the instructions in [gke-aiml Terraform module documentation](../terraform-modules/gke-aiml/README.md) 

In the second stage, the Saxml components, including admin servers, model servers, and http proxies are deployed to the GKE cluster. This stage is automated with **Skaffold** and **Kustomize**. 


> [!WARNING]
>  Your project must have sufficient [quota to provision TPU resources](https://cloud.google.com/tpu/docs/quota). Else, you can [request for a higher quota limit](https://cloud.google.com/docs/quota/view-manage#requesting_higher_quota).



### Configure pre-requisites

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
  - Set `location` to a location where you want to create the automation bucket 
  - Set `automation_sa_name` to the automation service account name in your environment
  - If you are going to configure the performance testing components uncomment the `services` and `roles` variables
5. Execute the `terraform init` command
6. Execute the `terraform apply` command

Besides enabling the necessary services and setting up an automation service account and an automation GCS bucket, the Terraform configuration has generated prepopulated template files for configuring the Terraform backend and providers, which can be utilized in the following setup stages. These template files are stored in the `gs://<YOUR-AUTOMATION-BUCKET/providers` folder.


#### Granting Cloud Build impersonating rights

To be able to impersonate the automation service account, the Cloud Build service account needs to have the `iam.serviceAccountTokenCreator` rights on the automation service account.

```shell
AUTOMATION_SERVICE_ACCOUNT=<AUTOMATTION_SERVICE_ACOUNT_EMAIL>
CLOUD_BUILD_SERVICE_ACCOUNT=<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com

gcloud iam service-accounts add-iam-policy-binding $AUTOMATION_SERVICE_ACCOUNT --member="serviceAccount:$CLOUD_BUILD_SERVICE_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'
```

Replace <PROJECT_NUMBER> with your project number. Replace <AUTOMATION_SERVICE_ACCOUNT_EMAIL> with the email of your automation service account. If you created the automation service account using the bootstrap Terraform you can retrieve its email by executing the `terraform output automation_sa` command from the `environment\0-bootstrap` folder.

### Deploy base infrastructure 

#### Clone the GitHub repo. 

If you haven't already run the bootstrap stage, please clone this repository now.

```bash
git clone https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples.git
```

Change the current directory, to `ai-infrastructure/saxml-on-gke/environment`.

#### Configure build parameters

If you used the `bootstrap` configuration to configure the prerequisites, copy the `providers\providers.tf` and `providers\backend.tf` files from the `providers` folder in your automation bucket to the `1-base-infrastructure` folder. Modify the `backend.tf` by setting the `prefix` field to the name of a folder in the automation bucket where you want to store your Terraform configuration's state. For example, if you want to manage the Terraform state in the `tf_state/gke_saxml` subfolder of the automation bucket set the `prefix` field to `tf_state/gke_saxml`.

If the automation bucket and the automation service account were provided to you by your administrator, rename the `backend.tf.tmpl` and the `providers.tf.tmpl` files to `backend.tf` and `providers.tf` and update them with your settings.

To configure the Terraform steps in the build, copy the `terraform.tfvars.tmpl` file in the `1-base-infrastructure` folder to `terraform.tfvars`. Make modifications to the `terraform.tfvars` file to align it with your specific environment. At the very least, you should set the following variables:

- `project_id` - your project ID
- `region` - your region for a VPC and a GKE cluster
- `prefix` - the prefix that will be added to the default names of resources provisioned by the configuration
- `tpu_node_pools` - The  template shows an example configuration for one TPU node pool with a v4-8 device. Modify the `tpu_node_pools` variable to provision different TPU node pool configurations, as described below.

If you wish to modify other default settings, such as the default name suffixes for a cluster or GCS bucket names, you can override the defaults specified in the `variables.tf` file within your `terraform.tfvars` file.

When configuring TPU node pools, ensure that you set the TPU type to one of the following values:

##### TPU types


| TPU type name | Slice type | Slice topology | TPU VM type | Number of VMs in a slice | Number of chips in a VM |
| ------------- | -----------|----------------|-------------|--------------------------| ------------------------|
|v5litepod-1|tpu-v5-lite-podslice|1x1|ct5lp-hightpu-1t|1|1|
|v5litepod-4|tpu-v5-lite-podslice|2x2|ct5lp-hightpu-4t|1|4|
|v5litepod-8|tpu-v5-lite-podslice|2x4|ct5lp-hightpu-8t|1|8|
|v5litepod-16|tpu-v5-lite-podslice|4x4|ct5lp-hightpu-4t|4|4|
|v5litepod-32|tpu-v5-lite-podslice|4x8|ct5lp-hightpu-4t|8|4|
|v5litepod-64|tpu-v5-lite-podslice|8x8|ct5lp-hightpu-4t|16|4|
|v5litepod-128|tpu-v5-lite-podslice|8x16|ct5lp-hightpu-4t|32|4|
|v5litepod-256|tpu-v5-lite-podslice|16x16|ct5lp-hightpu-4t|64|4|
|v4-8|tpu-v4-podslice|2x2x1|ct4p-hightpu-4t|1|4|
|v4-16|tpu-v4-podslice|2x2x2|ct4p-hightpu-4t|2|4|
|v4-32|tpu-v4-podslice|2x2x4|ct4p-hightpu-4t|4|4|
|v4-64|tpu-v4-podslice|2x4x4|ct4p-hightpu-4t|8|4|
|v4-128|tpu-v4-podslice|4x4x4|ct4p-hightpu-4t|16|4|

----------

#### Submit the build

To initiate the build, execute the following command:

```
gcloud builds submit \
  --config cloudbuild.provision.yaml \
  --timeout "2h" \
  --machine-type=e2-highcpu-32 
```


To track the progress of the build, you can either follow the link displayed in Cloud Shell or visit the Cloud Build page on the [Google Cloud Console](https://console.cloud.google.com/cloud-build).

The Cloud Build runs are annotated with the `saxml-infra-deployment` tags.

If you need to access the build logs after the build completes you can use this tag for filtering.

To list the builds:

```
gcloud builds list --filter "tags='saxml-infra-deployment'"
```

To retrieve the logs for a build:

```
gcloud builds log <BUILD_ID>
```

For your convenience, the final step of the build displays the names of all resources created during the build process. This makes it easier for you to retrieve them for configuring Saxml deployment and other workloads.


### Deploy Saxml components 

As an alternative to an automated deployment, you can run each stage of the setup individually.

If you haven't already, please clone this repository now.

```
git clone https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples.git
```

Change the current directory to `ai-infrastructure/saxml-on-gke/environment



#### Provision the base environment

The Terraform configuration in the `environment/1-base_environment` folder creates and configures all the necessary components for deploying and serving Saxml models, including a VPC, a GKE cluster, service accounts, CPU and TPU node pools, and storage buckets.

##### Configure the Terraform providers and state

If you used the `bootstrap` configuration to configure the prerequisites, copy the `providers\providers.tf` and `providers\backend.tf` files from the `providers` folder in your automation bucket to the `1-base_environment` folder in the cloned repo. Modify the `backend.tf` by setting the `prefix` field to the name of a folder in the automation bucket where you want to store your Terraform configuration's state. For example, if you want to manage the Terraform state in the `tf_state/saxml` subfolder of the automation bucket set the `prefix` field to `tf_state/saxml`.

If the automation bucket and the automation service account were provided to you by your administrator, rename the `backend.tf.tmpl` and the `providers.tf.tmpl` files to `backend.tf` and `providers.tf` and update them with your settings.

##### Configure Terraform variables

You need to set the input variables required by the Terraform configuration to reflect your environment. Rename the `terraform.tfvars.tmpl` file to `terraform.tfvars` and update the settings.

At a minimum, you need to configure the following settings:
- `project_id` - your project ID
- `region` - your region. All components of the base environment will be provisioned in this region
- `prefix` - the prefix that will be added to the predefined names of resources provisioned by the configuration
- `artifact_registry_name` - the name of an Artifact Registry to provision. If you want to use an existing Artifact registry delete this variable 
- `tpu_node_pools` - The `terraform.tfvars.tmpl` template provides an example configuration for a single TPU node pool with one v4-8 node. Modify the `tpu_node_pools` variable to provision different TPU node pool configurations, as described below.

With these minimal settings, the Terraform configuration will provision an environment as described in the High-Level Architecture section. Default settings for the environment's components, such as GCS, VPC and node pool configurations, are defined in the [variables.tf](environment/1-base_environment/variables.tf) file.

If you want to make changes to the default configuration override the default values in the `terraform.tfvars` file.

The Terraform configuration for the base environment utilizes the [gke-aiml](/ai-infrastructure/terraform-modules/gke-aiml/) Terraform module. If you need to make modifications beyond changing variable defaults, please refer to the module's documentation.


##### Apply the configuration

```
terraform init
terraform apply
```

#### Set cluster credentials

Set credentials to access your GKE cluster. You can retrieve the cluster name and the cluster region by executing terraform output cluster_name and terraform output region from the environment\1-base_environment folder.

```
gcloud container clusters get-credentials <CLUSTER_NAME> --region <REGION>
```

Replace <CLUSTER_NAME> with the name of your GKE cluster and <REGION> with the region of your GKE cluster.

##### Create a namespace and a Kubernetes service account

To finalize the installation of the base environment, create a namespace where Saxml components will be deployed. You also need to create a Kubernetes service account that will be employed with Workload Identity. This service account should be configured to act as an IAM service account generated by the Terraform configuration executed in the preceding step.

To create a namespace, execute the following command:

```
kubectl create namespace <NAMESPACE_NAME>
```

Replace `<NAMESPACE_NAME>`` with the name of the namespace used to annotate the IAM service account. You can retrieve the namespace using the `terraform output wid_ksa_namespace` command. 


To create a service account, execute the following commands:

```
kubectl create serviceaccount <KSA_NAME> -n <NAMESPACE_NAME>
kubectl annotate serviceaccount <KSA_NAME> "iam.gke.io/gcp-service-account=<IAM_SA_EMAIL>" -n <NAMESPACE_NAME>
```

Replace `<KSA_NAME>`` with the KSA name used to annotate the IAM service account. You can retrieve the KSA name using the `terraform output wid_ksa_name` command.  Replace `<IAM_SA_NAME>` with the email of the IAM service account. You can retrieve the email using the `terraform output wid_gsa_email` command.




#### Deploy the Saxml inference system

After the base infrastructure has been provisioned you can deploy Saxml components to your GKE cluster. The deployment process has been automated with **Skaffold** and **Kustomize**. You can find the Kustomize configuration in the `environment/2-saxml/manifests` folder. 

 Update the `kustomization.yaml` with the namespace created during the base environment setup. This namespace will be used to deploy Saxml components. You can retrieve the namespace name by executing `terraform output namespace` from the `environment\1-base_environment` folder.

From the `environment/2-saxml/saxml_manifests` folder run:
```
kustomize edit set namespace <SAXML_NAMESPACE> 
```

Replace `<SAXML_NAMESPACE>` with the name of the namespace created during the base environment setup.

Update the `parameters.env` to reflect your desired configuration

- `GSBUCKET` - the name of the Saxml admint bucket. You can retrieve the name of the bucket by executing `terraform output gcs_buckets` from the `environment\1-base_environment` folder. 
- `KSA` - the Kubernetes service account to use for Workload Identity. You can retrieve the name of the account by executing `terraform output ksa_name` from the `environment\1-base_environment` folder.  
- `SAX_CELL` - the name of the Sax cell. Currently, it is hardcoded to `/sax/test`.
- `SAX_ROOT` - the path in the Saxml admin bucket to the root folder. Update the bucket name with the name of your admin bucket - `GSBUCKET`
- `TPU_CHIP` - the TPU chip type  
- `TPU_TYPE` - the TPU pod slice type
- `TPU_TOPOLOGY` - the topology of the TPU slice
- `CHIPS_PER_NODE` - the number of TPU chips on the host node

Set credentials to access your GKE cluster. You can retrieve the cluster name and the cluster region by executing `terraform output cluster_name` and `terraform output region` from the `environment\1-base_environment` folder.

```
gcloud container clusters get-credentials <CLUSTER_NAME> --region <REGION>
```

Replace `<CLUSTER_NAME>` with the name of your GKE cluster and `<REGION>` with the region of your GKE cluster.

To deploy the Saxml components run the following command from the `environment/2-saxml/` folder:

```
skaffold run --default-repo <ARTIFACT_REGISTRY_PATH> --profile cloudbuild
```

Replace <ARTIFACT_REGISTRY> with the path to your Artifact Registry. If you created an Artifact Registry during the base environment setup you can retrieve the path by executing `terraform output artifact_registry_image_path`` from the `environment\1-base_environment` folder

The above command built container images and deployed Saxml servers and utilities to the cluster. Verify that all pods have started successfully:

```
kubectl get pods -n <SAXML_NAMESPACE>
```



#### Provisioning performance testing components

This stage is optional. If you plan to conduct performance tests using the [Load Generator](environment/3-load_generator/locust_load_generator/) tool, you must configure the Pubsub and BigQuery services to enable test metrics tracking and analysis.

The Terraform configuration for the performance testing environment is in the `environment/3-load_generation/terraform` folder.

##### Configure the Terraform providers and state

Follow the process outlined in the previous section to configure the `backend.tf` and `providers.tf` files.

##### Configure Terraform variables

Rename the `terraform.tfvars.tmpl` file to `terraform.tfvars` and update it to match your environment settings.

At a minimum, you need to configure the following settings:
- `project_id` - your project ID
- `region` - your region. All load testing components will be provisioned in this region
- `prefix` - the prefix that will be added to the predefined names of resources provisioned by the configuration

With these settings, the Terraform configuration will use predefined names from the [variables.tf](environment/3-load_generator/terraform/variables.tf) file for Pubsub and BigQuery components, with the prefix added to the name of each resource. If you want to change the default names, override them in the `terraform.tfvars` file.

##### Apply the configuration

```
terraform init
terraform apply
```


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
terraform state rm module.base_environment.kubernetes_namespace.namespace[0]
```


#### Bootstrap

If you provisioned the prerequistes using the bootstrap configuration you can optionally remove the automation account and the automation bucket.

From the `0-bootstrap` folder:

```
terraform destroy
```




