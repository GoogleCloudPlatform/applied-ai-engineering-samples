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

The deployment process is automated using [Cloud Build](https://cloud.google.com/build), [Terraform](https://cloud.google.com/docs/terraform),  [Kustomize](https://kustomize.io/), and [Skaffold](https://skaffold.dev/). 
To run the setup and execute code samples, you will need a workstation with [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk), [Terraform](https://www.terraform.io/), [Kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize), [Skaffold](https://skaffold.dev), and [kubectl](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl) utilities. We recommend using [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell), which has all the utilities pre-installed.



The first stage is automated with **Cloud Build** and **Terraform**. The **Cloud Build** configuration orchestrates the following steps:

- [ ] Creates a network, a subnet, and IP ranges for GKE pods and services.
- [ ] Creates a VPC-native cluster.
- [ ] Creates CPU node pools.
- [ ] Creates TPU node pools.
- [ ] Creates an IAM service account for Workload Identity and an IAM service account to be used as a custom node pool service account.
- [ ] Configures the cluster for Workload Identity.
- [ ] Creates a Kubernetes namespace to host Saxml servers and a Kubernetes service account to use with Workload Identity
- [ ] Creates two Google Cloud Storage buckets. One to be used as a Saxml admin bucket. The other to manage serving checkpoints and other serving artifacts.
- [ ] Creates an Artifact Registry
- [ ] Creates a BigQuery dataset and table 
- [ ] Creates a Pubsub topic and BigQuery subscription

The last three steps are optional. They can be skipped by setting the `create_artifact_registry` and the `create_perf_testing_infrastructure` Terraform input variables to `false`. Refer to the below instructions on updating Terraform input variables.

The Terraform configuration creates and configures a new VPC  by default. However, you can also opt to use an existing VPC for a GKE cluster, as this functionality is supported by the [gke-aiml Terraform module](../terraform-modules/gke-aiml/README.md), which is used by the Terraform configuration.

To use an existing VPC you need to modify the inputs to the `module "base_environment"` in the `environment/1-base-infrastrucutre/main.tf` file, following the instructions in the [gke-aiml Terraform module documentation](../terraform-modules/gke-aiml/README.md) 

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

The prerequisites may need to be configured by your GCP organization administrator. If you have access to a project where you are a project owner, you can configure the prerequisites using the Terraform configuration in the [environment/0-bootstrap](environment/0-bootstrap/) folder.

1. Clone this repo
2. Change the current folder to [environment/0-bootstrap](environment/0-bootstrap/)
3. Copy the [terraform.tfvars.tmpl](environment/0-bootstrap/terraform.tfvars.tmpl) file to `terraform.tfvars`
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

Replace <PROJECT_NUMBER> with your project number. Replace <AUTOMATION_SERVICE_ACCOUNT_EMAIL> with the email of your automation service account. If you created the automation service account using the bootstrap Terraform you can retrieve its email by executing the `terraform output automation_sa` command from the [environment\0-bootstrap](environment/0-bootstrap/) folder.

### Deploy base infrastructure 

#### Clone the GitHub repo. 

If you haven't already run the bootstrap stage, please clone this repository now.

```bash
git clone https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples.git
```

Change the current directory, to [environment](environment/).

#### Configure build parameters

If you used the `bootstrap` configuration to configure the prerequisites, copy the `providers\providers.tf` and `providers\backend.tf` files from the `providers` folder in your automation bucket to the [1-base-infrastructure](environment/1-base-infrastructure/) folder. Modify the `backend.tf` by setting the `prefix` field to the name of a folder in the automation bucket where you want to store your Terraform configuration's state. For example, if you want to manage the Terraform state in the `tf_state/gke_saxml` subfolder of the automation bucket set the `prefix` field to `tf_state/gke_saxml`.

If the automation bucket and the automation service account were provided to you by your administrator, rename the `backend.tf.tmpl` and the `providers.tf.tmpl` files to `backend.tf` and `providers.tf` and update them with your settings.

To configure the Terraform steps in the build, copy the [terraform.tfvars.tmpl](environment/1-base-infrastructure/terraform.tfvars.tmpl) template file in the [1-base-infrastructure](environment/1-base-infrastructure/) folder to `terraform.tfvars`. Make modifications to the `terraform.tfvars` file to align it with your specific environment. At the very least, you should set the following variables:

- `project_id` - your project ID
- `region` - your region for a VPC and a GKE cluster
- `prefix` - the prefix that will be added to the default names of resources provisioned by the configuration
- `tpu_node_pools` - The  template shows an example configuration for one TPU node pool with a single `v5litepod-4` slice. Modify the `tpu_node_pools` variable to provision different TPU node pool configurations, as described below.
- `cput_node_pools` - The template shows an example configuration for a number of CPU node pools as outlined in the [High Level Architecture section](#high-level-architecture)  

If you wish to modify other default settings, such as the default name suffixes for a cluster or GCS bucket names, you can override the defaults specified in the [variables.tf](environment/1-base-infrastructure/variables.tf) file within your `terraform.tfvars` file.

When configuring TPU node pools, ensure that you set the TPU type to one of the following values:

##### TPU types


| TPU type name | TPU chip|  Slice type | Slice topology | TPU VM type | Number of VMs in a slice | Number of chips in a VM |
| ------------- | ---------| -----------|----------------|-------------|--------------------------| ------------------------|
|v5litepod-1| tpuv5e| tpu-v5-lite-podslice|1x1|ct5lp-hightpu-1t|1|1|
|v5litepod-4|tpuv5e|tpu-v5-lite-podslice|2x2|ct5lp-hightpu-4t|1|4|
|v5litepod-8|tpuv5e|tpu-v5-lite-podslice|2x4|ct5lp-hightpu-8t|1|8|
|v5litepod-16|tpuv5e|tpu-v5-lite-podslice|4x4|ct5lp-hightpu-4t|4|4|
|v5litepod-32|tpuv5e|tpu-v5-lite-podslice|4x8|ct5lp-hightpu-4t|8|4|
|v5litepod-64|tpuv5e|tpu-v5-lite-podslice|8x8|ct5lp-hightpu-4t|16|4|
|v5litepod-128|tpuv5e|tpu-v5-lite-podslice|8x16|ct5lp-hightpu-4t|32|4|
|v5litepod-256|tpuv5e|tpu-v5-lite-podslice|16x16|ct5lp-hightpu-4t|64|4|
|v4-8|tpuv4|tpu-v4-podslice|2x2x1|ct4p-hightpu-4t|1|4|
|v4-16|tpuv4|tpu-v4-podslice|2x2x2|ct4p-hightpu-4t|2|4|
|v4-32|tpuv4|tpu-v4-podslice|2x2x4|ct4p-hightpu-4t|4|4|
|v4-64|tpuv4|tpu-v4-podslice|2x4x4|ct4p-hightpu-4t|8|4|
|v4-128|tpuv4|tpu-v4-podslice|4x4x4|ct4p-hightpu-4t|16|4|

----------

#### Submit the build

To initiate the build, execute the following command from the [environment](environment/) folder:

```
export AUTOMATION_BUCKET=<YOUR_AUTOMATION_BUCKET>

gcloud builds submit \
  --config cloudbuild.provision.yaml \
  --timeout "2h" \
  --substitutions=_AUTOMATION_BUCKET=$AUTOMATION_BUCKET \
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

Once the base infrastructure has been provisioned, you can proceed to deploy Saxml components on your GKE cluster. This deployment process has been automated using [Skaffold](https://skaffold.dev) and [Kustomize](https://kustomize.io). You'll find the manifests, source code, and other deployment artifacts in the [environment/2-workloads/saxml](environment/2-workloads/saxml/) folder.

#### Update Kustomize settings

From the [environment/2-workloads/saxml/manifests](environment/2-workloads/saxml/manifests/) folder:

```
kustomize edit set namespace <NAMESPACE>
```

Replace `<NAMESPACE>` with the name of the namespace established during the base infrastructure setup. Remember that you can retrieve the names of all the provisioned resources, including the namespace name, from the build logs.

Copy the [parameters.env.tmpl](environment/2-workloads/saxml/manifests/parameters.env.tmpl) file to `parameters.env`.

Update the `parameters.env` to reflect your desired configuration

- `GSBUCKET` - the name of the Saxml admint bucket.
- `KSA` - the Kubernetes service account to use for Workload Identity. 
- `SAX_CELL` - the name of the Sax cell. Currently, it is hardcoded to `/sax/test`.
- `SAX_ROOT` - the path in the Saxml admin bucket to the root folder. Update the bucket name with the name of your admin bucket - `GSBUCKET`
- `TPU_CHIP` - the TPU chip type  
- `TPU_SLICE_TYPE` - the TPU pod slice type
- `TPU_SLICE_TOPOLOGY` - the topology of the TPU slice
- `CHIPS_PER_NODE` - the number of TPU chips on the host node

You can find the values for `TPU_CHIP`, `TPU_SLICE_TYPE`, `TPU_SLICE_TOPOLOGY`, and `CHIPS_PER_NODE` in your configuration by referring to the [TPU types table](#tpu-types).

#### Get cluster credentials

Set credentials to access your GKE cluster. 

```
gcloud container clusters get-credentials <CLUSTER_NAME> --region <REGION>
```

Replace `<CLUSTER_NAME>` with the name of your GKE cluster and `<REGION>` with the region of your GKE cluster.

#### Deploy Saxml 

To build and push the container packaging the Saxml proxy to your Artifact Registry, and to deploy Saxml components, execute the following command from the [environment/2-workloads/saxml](environment/2-workloads/saxml/) folder:


```
skaffold run --default-repo <ARTIFACT_REGISTRY_PATH> --profile cloudbuild
```

Replace `<ARTIFACT_REGISTRY>` with the path to your Artifact Registry. 

Verify that all pods have started successfully:

```
kubectl get pods -n <SAXML_NAMESPACE>
```


#### Undeploy Saxml

If you wish to undeploy the Saxml components, run the following command from the [environment/2-workloads/saxml](environment/2-workloads/saxml/) folder:

```
skaffold delete
```

### Deploying Saxml models

This repository contains comprehensive examples for deploying and performance testing various Generative AI models, including Llama2, 7B, 13B, and 70B. For detailed instructions, please refer to the [Examples section](/ai-infrastructure/saxml-on-gke/examples/README.md) of the repository.

### Destroying the environment

#### Base infrastructure

From the [environment](environment/) folder.

```

export AUTOMATION_BUCKET=<YOUR_AUTOMATION_BUCKET>

gcloud builds submit \
  --config cloudbuild.destroy.yaml \
  --timeout "2h" \
  --substitutions=_AUTOMATION_BUCKET=$AUTOMATION_BUCKET \
  --machine-type=e2-highcpu-32 
```


#### Bootstrap

To clean up the automation bootstrap resources.

From the [environment](environment/0-bootstrap/) folder:

```
terraform destroy
```




