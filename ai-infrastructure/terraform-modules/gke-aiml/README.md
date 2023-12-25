#  GKE for Large Model Training and Serving 

his Terraform module configures a GKE-based infrastructure environment specifically designed for training and serving large and extremely large deep learning models, including the most recent Generative AI models.

The central element of this environment is a VPC-native GKE Standard cluster. This cluster is configured to utilize Workload Identity. Users of the module can decide whether to deploy the cluster within an existing VPC or create a new VPC specifically for the cluster. The cluster can be configured with multiple CPU and TPU node pools. The node pools use a custom service account. This service account can be an existing one or a newly created account.

Beyond the cluster, users have the option to create additional services such as Artifact Registry or Cloud Storage buckets.


The module carries out the following tasks:
- If a reference to an existing VPC is not provided, it will create a network, a subnet, and IP ranges for GKE pods and services.
- Optionally, it can provision [Cloud NAT](https://cloud.google.com/nat/docs/overview)
- If a reference to an existing service account is not provided, the module will create a new service account and assign it to a user-defined set of security roles.
- Creates a user defined number of CPU node pools
- Creates a user defined number of TPU node pools
- The node pools are configured to use a custom service account
- Provisions a standard, VPC-native GKE cluster.
- Deploys a standard, VPC-native GKE cluster that is configured to utilize Workload Identity.
- Optionally, it can create an Artifact Registry.
- Creates the specified number of user-defined Cloud Storage buckets.

## Examples

### GKE TPU training environment

This example demonstrates how to configure an environment optimized for executing large-scale training workloads on TPUs. In this sample, a new VPC, a new service account, and a new Artifact Registry are created. All resources are generated using default values for the majority of the settings.

```
module "tpu-training-cluster" {
    source     = "github.com/GoogleCloudPlatform/applied-ai-engineering-samples//ai-infrastructure/terraform-modules/gke-aiml
    project_id = "project_id"
    region     = "us-central2"
    vpc_config = {
        network_name = "gke-cluster-network"
        subnet_name  = "gke-cluster-subnetwork"
    }
    node_pool_sa = {
        name = "gke-node-pool-sa"
    }
    cluster_config = {
        name = "gke-tpu-training-cluster"
    }
    cpu_node_pools = {
        default-cpu-node-pool = {
            zones  = ["us-central2-a"]
            labels = {
                default-node-pool=true
            }
        }
    }
    tpu_node_pools = {
        tpu-v4-16-podslice-1 = {
            zones    = ["us-central2-b"]
            tpu_type = "v4-16"
        }
        tpu-v4-16-podslice-2 = {
           zones    = ["us-central2-b"]
            tpu_type = "v4-16"
        }
    }
    gcs_configs = {
      training-artifacts-bucket = {} 
    }
    registry_config = {
        name     = "training-images"
        location = "us"
    }
}
```

## Variables

| Name | Description | Type | Required | Default |
|---|---|---|---|---|
|[project_id](variables.tf#L16)| Environment project ID|`string`| &check; ||
|[region](variables.tf#L22)| Environment region|`string`|&check;||
|[deletion_protection](variables.tf#L28)|Prevent Terraform from destroying data storage resources (storage buckets, GKE clusters). When this field is set, a terraform destroy or terraform apply that would delete data storage resources will fail.|`string`||`true`|
|[cluster_config](variables.tf#L106)|Cluster level configurations|`object({...})`||`{...}`|
|[vpc_config](variables.tf#L90)|Network configurations of a VPC to create. Must be specified if vpc_reg is null|`object({...})`||`{...}`|
|[vpc_ref](variables.tf#L78)|Settings for the  existing VPC to use for the environment. If null, a new VPC based on the `vpc_config` will be created|`object({...})`||`{...}`|
|[node_pool_sa](variables.tf#L57)|Settings for a node pool service account|`object({...})`||`{...}`|
|[cpu_node_pools](variables.tf#L125)|Settings for CPU node pools|`map(object({...}))`||`{...}`|
|[tpu_node_pools](variables.tf#L156)|Settings for TPU node pools. See below for more information about TPU slice types|`map(object({...}))`||`{...}`|
|[gcs_configs](variables.tf#L35)|Settings for Cloud Storage buckets|`map(object({...}))`||`{...}`|
|[registry_config](variables.tf#47)|Settings for Artifact Registry|`object({...})`||`{...}`|


### Specifying TPU type

When configuring TPU node pools, ensure that you set the TPU type to one of the following values:



| TPU type name | Slice type | Slice topology | TPU VM type | Number of VMs in a slice | Number of chips in a VM |
| ------------- | -----------|----------------|-------------|--------------------------| ------------------------|
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
|v4-256|tpu-v4-podslice|4x4x8|ct4p-hightpu-4t|32|4|
|v4-512|tpu-v4-podslice|4x8x8|ct4p-hightpu-4t|64|4|
|v4-1024|tpu-v4-podslice|8x8x8|ct4p-hightpu-4t|128|4|
|v4-1536|tpu-v4-podslice|8x8x12|ct4p-hightpu-4t|192|4|
|v4-2048|tpu-v4-podslice|8x8x16|ct4p-hightpu-4t|256|4|
|v4-4096|tpu-v4-podslice|8x16x16|ct4p-hightpu-4t|512|4|
|v5p-8|tpu-v5p-slice|2x2x1|ct5p-hightpu-4t|1|4|
|v5p-16|tpu-v5p-slice|2x2x2|ct5p-hightpu-4t|2|4|
|v5p-32|tpu-v5p-slice|2x2x4|ct5p-hightpu-4t|4|4|
|v5p-64|tpu-v5p-slice|2x4x4|ct5p-hightpu-4t|8|4|
|v5p-128|tpu-v5p-slice|4x4x4|ct5p-hightpu-4t|16|4|
|v5p-256|tpu-v5p-slice|4x4x8|ct5p-hightpu-4t|32|4|
|v5p-384|tpu-v5p-slice|4x4x12|ct5p-hightpu-4t|48|4|
|v5p-512|tpu-v5p-slice|4x8x8|ct5p-hightpu-4t|64|4|
|v5p-640|tpu-v5p-slice|4x4x20|ct5p-hightpu-4t|80|4|
|v5p-768|tpu-v5p-slice|4x8x12|ct5p-hightpu-4t|96|4|
|v5p-896|tpu-v5p-slice|4x4x28|ct5p-hightpu-4t|112|4|
|v5p-1024|tpu-v5p-slice|8x8x8|ct5p-hightpu-4t|128|4|
|v5p-1152|tpu-v5p-slice|4x12x12|ct5p-hightpu-4t|144|4|
|v5p-1280|tpu-v5p-slice|4x8x20|ct5p-hightpu-4t|160|4|
|v5p-1408|tpu-v5p-slice|4x4x44|ct5p-hightpu-4t|176|4|
|v5p-1536|tpu-v5p-slice|8x8x12|ct5p-hightpu-4t|192|4|
|v5p-1664|tpu-v5p-slice|4x4x52|ct5p-hightpu-4t|208|4|
|v5p-1792|tpu-v5p-slice|4x8x28|ct5p-hightpu-4t|224|4|
|v5p-1920|tpu-v5p-slice|4x12x20|ct5p-hightpu-4t|240|4|
|v5p-2048|tpu-v5p-slice|8x8x16|ct5p-hightpu-4t|256|4|
|v5p-2176|tpu-v5p-slice|4x4x68|ct5p-hightpu-4t|272|4|
|v5p-2304|tpu-v5p-slice|8x12x12|ct5p-hightpu-4t|288|4|
|v5p-2432|tpu-v5p-slice|4x4x76|ct5p-hightpu-4t|304|4|
|v5p-2560|tpu-v5p-slice|8x8x20|ct5p-hightpu-4t|320|4|
|v5p-2688|tpu-v5p-slice|4x12x28|ct5p-hightpu-4t|336|4|
|v5p-2816|tpu-v5p-slice|4x8x44|ct5p-hightpu-4t|352|4|
|v5p-2944|tpu-v5p-slice|4x4x92|ct5p-hightpu-4t|368|4|
|v5p-3072|tpu-v5p-slice|4x12x16|ct5p-hightpu-4t|384|4|
|v5p-3200|tpu-v5p-slice|4x20x20|ct5p-hightpu-4t|400|4|
|v5p-3328|tpu-v5p-slice|4x8x52|ct5p-hightpu-4t|416|4|
|v5p-3456|tpu-v5p-slice|12x12x12|ct5p-hightpu-4t|432|4|
|v5p-3584|tpu-v5p-slice|8x8x28|ct5p-hightpu-4t|448|4|
|v5p-3712|tpu-v5p-slice|4x4x116|ct5p-hightpu-4t|464|4|
|v5p-3840|tpu-v5p-slice|8x12x20|ct5p-hightpu-4t|480|4|
|v5p-3968|tpu-v5p-slice|4x4x124|ct5p-hightpu-4t|496|4|
|v5p-4096|tpu-v5p-slice|8x16x16|ct5p-hightpu-4t|512|4|
|v5p-4224|tpu-v5p-slice|4x12x44|ct5p-hightpu-4t|528|4|
|v5p-4352|tpu-v5p-slice|4x8x68|ct5p-hightpu-4t|544|4|
|v5p-4480|tpu-v5p-slice|4x20x28|ct5p-hightpu-4t|560|4|
|v5p-4608|tpu-v5p-slice|12x12x16|ct5p-hightpu-4t|576|4|
|v5p-4736|tpu-v5p-slice|4x4x148|ct5p-hightpu-4t|592|4|
|v5p-4864|tpu-v5p-slice|4x8x76|ct5p-hightpu-4t|608|4|
|v5p-4992|tpu-v5p-slice|4x12x52|ct5p-hightpu-4t|624|4|
|v5p-5120|tpu-v5p-slice|8x16x20|ct5p-hightpu-4t|640|4|
|v5p-5248|tpu-v5p-slice|4x4x164|ct5p-hightpu-4t|656|4|
|v5p-5376|tpu-v5p-slice|8x12x28|ct5p-hightpu-4t|672|4|
|v5p-5504|tpu-v5p-slice|4x4x172|ct5p-hightpu-4t|688|4|
|v5p-5632|tpu-v5p-slice|8x8x44|ct5p-hightpu-4t|704|4|
|v5p-5760|tpu-v5p-slice|12x12x20|ct5p-hightpu-4t|720|4|
|v5p-5888|tpu-v5p-slice|4x8x92|ct5p-hightpu-4t|736|4|
|v5p-6016|tpu-v5p-slice|4x4x188|ct5p-hightpu-4t|752|4|
|v5p-6144|tpu-v5p-slice|12x16x16|ct5p-hightpu-4t|768|4|
|v5p-6272|tpu-v5p-slice|4x28x28|ct5p-hightpu-4t|784|4|
|v5p-6400|tpu-v5p-slice|8x20x20|ct5p-hightpu-4t|800|4|
|v5p-6528|tpu-v5p-slice|4x12x68|ct5p-hightpu-4t|816|4|
|v5p-6656|tpu-v5p-slice|8x8x52|ct5p-hightpu-4t|832|4|
|v5p-6784|tpu-v5p-slice|4x4x212|ct5p-hightpu-4t|848|4|
|v5p-6912|tpu-v5p-slice|12x12x24|ct5p-hightpu-4t|864|4|
|v5p-7040|tpu-v5p-slice|4x20x44|ct5p-hightpu-4t|880|4|
|v5p-7168|tpu-v5p-slice|8x16x28|ct5p-hightpu-4t|896|4|
|v5p-7296|tpu-v5p-slice|4x12x76|ct5p-hightpu-4t|912|4|
|v5p-7424|tpu-v5p-slice|4x8x116|ct5p-hightpu-4t|928|4|
|v5p-7552|tpu-v5p-slice|4x4x236|ct5p-hightpu-4t|944|4|
|v5p-7680|tpu-v5p-slice|12x16x20|ct5p-hightpu-4t|960|4|
|v5p-7808|tpu-v5p-slice|4x4x244|ct5p-hightpu-4t|976|4|
|v5p-7936|tpu-v5p-slice|4x8x124|ct5p-hightpu-4t|992|4|
|v5p-8064|tpu-v5p-slice|12x12x28|ct5p-hightpu-4t|1008|4|
|v5p-8192|tpu-v5p-slice|16x16x16|ct5p-hightpu-4t|1024|4|
|v5p-8320|tpu-v5p-slice|4x20x52|ct5p-hightpu-4t|1040|4|
|v5p-8448|tpu-v5p-slice|8x12x44|ct5p-hightpu-4t|1056|4|
|v5p-8704|tpu-v5p-slice|8x8x68|ct5p-hightpu-4t|1088|4|
|v5p-8832|tpu-v5p-slice|4x12x92|ct5p-hightpu-4t|1104|4|
|v5p-8960|tpu-v5p-slice|8x20x28|ct5p-hightpu-4t|1120|4|
|v5p-9216|tpu-v5p-slice|12x16x24|ct5p-hightpu-4t|1152|4|
|v5p-9472|tpu-v5p-slice|4x8x148|ct5p-hightpu-4t|1184|4|
|v5p-9600|tpu-v5p-slice|12x20x20|ct5p-hightpu-4t|1200|4|
|v5p-9728|tpu-v5p-slice|8x8x76|ct5p-hightpu-4t|1216|4|
|v5p-9856|tpu-v5p-slice|4x28x44|ct5p-hightpu-4t|1232|4|
|v5p-9984|tpu-v5p-slice|8x12x52|ct5p-hightpu-4t|1248|4|
|v5p-10240|tpu-v5p-slice|16x16x20|ct5p-hightpu-4t|1280|4|
|v5p-10368|tpu-v5p-slice|12x12x36|ct5p-hightpu-4t|1296|4|
|v5p-10496|tpu-v5p-slice|4x8x164|ct5p-hightpu-4t|1312|4|
|v5p-10752|tpu-v5p-slice|12x16x28|ct5p-hightpu-4t|1344|4|
|v5p-10880|tpu-v5p-slice|4x20x68|ct5p-hightpu-4t|1360|4|
|v5p-11008|tpu-v5p-slice|4x8x172|ct5p-hightpu-4t|1376|4|
|v5p-11136|tpu-v5p-slice|4x12x116|ct5p-hightpu-4t|1392|4|
|v5p-11264|tpu-v5p-slice|8x16x44|ct5p-hightpu-4t|1408|4|
|v5p-11520|tpu-v5p-slice|12x20x24|ct5p-hightpu-4t|1440|4|
|v5p-11648|tpu-v5p-slice|4x28x52|ct5p-hightpu-4t|1456|4|
|v5p-11776|tpu-v5p-slice|8x8x92|ct5p-hightpu-4t|1472|4|
|v5p-11904|tpu-v5p-slice|4x12x124|ct5p-hightpu-4t|1488|4|
|v5p-12032|tpu-v5p-slice|4x8x188|ct5p-hightpu-4t|1504|4|
|v5p-12160|tpu-v5p-slice|4x20x76|ct5p-hightpu-4t|1520|4|
|v5p-12288|tpu-v5p-slice|16x16x24|ct5p-hightpu-4t|1536|4|
|v5p-13824|tpu-v5p-slice|12x24x24|ct5p-hightpu-4t|1728|4|
|v5p-17920|tpu-v5p-slice|16x20x28|ct5p-hightpu-4t|2240|4|


## Outputs

| Name | Description | 
|---|---|
|[node_pool_sa_email](outputs.tf#L16)|The email of the node pool sa|
|[cluster_name](outputs.tf#L21)|The name of the GKE cluster|
|[cluster_region](outputs.tf#L26)|The region of the GKE cluster|
|[gcs_buckets](outputs.tf#L31)|The names and locations of the created GCS buckets|
|[artifact_registry_id](outputs.tf#L38)|The full ID of the created Arifact Registry|
|[artifact_registry_image_path](outputs.tf#L43)|Artifact Registry path|




