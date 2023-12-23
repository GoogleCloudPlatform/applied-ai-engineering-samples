# Running TPU workloads with xpk

**xpk** [(Accelerated Processing Kit, pronounced x-p-k)](https://github.com/google/maxtext/tree/main/xpk) is a Python based tool designed to help Cloud developers to orchestrate training jobs on accelerators such as TPUs and GPUs on GKE. 

There are two set of examples in this folder showing how to configure and run training workloads using **xpk**:

- Experimenting with different data and model parallelism strategies with in single slice and multislice TPU configurations.
- Pre-training a MaxText 6.5B parameter model in both single slice and multislice TPU configurations.

**xpk** provides a simple command-line interface for managing GKE clusters and submitting training workloads that are encapsulated as JobSet configurations. In this reference guide, we do not use its cluster management capabilities. We use **xpk** to configure and submit training workloads to the GKE-based training environment provisioned during the setup.

Refer to the [xpk documentation](https://github.com/google/xpk) for detailed information on how to create, delete, and list workloads.

## Setup

### Install xpk

```
pip install xpk
```

### Update Kueue configuration

**xpk** uses [JobSet](https://github.com/kubernetes-sigs/jobset) and [Kueue](https://kueue.sigs.k8s.io/docs/overview/) for running training workloads. It assumes that there is a LocalQueue named `multislice-queue` in the `default` namespace and submits workloads to this queue. 

If you employed the automated setup with the default settings, a local queue named `tpu-job-queue` was created within the `tpu-training` namespace. To use **xpk** with the default environment, you should create a new local queue in the `default` namespace.


```bash
cat <<EOF >./local-queue.yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  namespace: default 
  name: multislice-queue
spec:
  clusterQueue: cluster-queue 
EOF

kubectl apply -f local-queue.yaml
```


### **xpk** and container images

By default, when xpk prepares a workload it layers the local directory (`--script-dir`) into the base docker image, uploads the updated image to your project's Container Registry, and references the uploaded image in the JobSet template. You can specify the base docker image through the `--base-docker-image` parameter. If you do not specify the base image, xpk attempts to create one using the default settings embedded in `xpk.py`. **xpk** relies on the local installation of **docker**.

If you don't want this layering behavior, you can specify the image to use through the `--docker-image` parameter.

In our examples, we will set the `--base-docker-image` to the [MaxText training image](../README.md) build as part of prerequisites for running examples. Make sure that you have a working installation of **docker** before running the below examples.

Recall that if you utilized the automated setup with the default settings, the path to your Artifact Registry is:

```
us-docker.pkg.dev/<YOUR_PROJECT_ID>/<YOUR_PREFIX>-training-images
```

And the MaxText training image URI is:

```
us-docker.pkg.dev/<YOUR_PROJECT_ID>/<YOUR_PREFIX>-training-images/maxtext-runner:latest
```

### Set the project id and the default zone

The majority of **xpk** commands require the use of the `zone` parameter. **xpk** relies on the `zone` parameter to locate your clusters, even for regional clusters, as it derives the region information from the specified zone.

If you have already configured the default zone and project ID for the Cloud SDK, there's no need to explicitly provide them when executing xpk commands.

```
gcloud config set project <PROJECT_ID>
gcloud config set compute/zone <ZONE>
```

Replace:
- `<PROJECT_ID>` - With your project ID
- `<ZONE>` - If your cluster is zonal, set it to your cluster's zone. However, if your cluster is regional, like the one provisioned by the automated setup, set it to one of the zones within the cluster's region where the node pools are provisioned.


### Running **xpk** smoke test

To ensure that your setup is correct and that you can successfully run **xpk** workloads, we will submit a simple smoke test workload to your cluster.

Set the current directory to:

```
cd <REPO_ROOT_DIR>/ai-infrastructure/tpu-training-on-gke/examples/xpk
```

Replace `<REPO_ROOT_DIR>` with the full path to the root of the cloned repo.

Run the following command:

```bash
xpk workload create \
--workload <WORKLOAD_ID> \
--base-docker-image <MAX_TEXT_IMAGE_URI> \
--cluster <CLUSTER_NAME> \
--tpu-type <TPU_TYPE> \
--command "echo Hello World" 
```

Replace the following values:
- `<WORKLOAD_ID>` - Choose a unique name for the workload. **xpk** will utilize this name when generating the name of a JobSet resource.
- `<MAX_TEXT_IMAGE_URI>` - Set to the URI of the MaxText  container image. E.g. `us-docker.pkg.dev/<YOUR_PROJECT_ID>/<YOUR_PREFIX>-training-images/maxtext-runner:latest` 
- `<CLUSTER_NAME>` - Replace with your cluster name
- `<TPU_TYPE>` - Specify the TPU type of one of your TPU node pools. Note that **xpk** follows the same TPU type naming convention as used during the setup, and defined in the [TPU Type table](../../README.md#tpu-types).

In the command's output, you'll notice that xpk is constructing a container image by utilizing the MaxText image as its base and including the contents of the current directory within the image. After successfully building and pushing the image to the Artifact Registry, xpk proceeds to create and submit a JobSet workload. Additionally, it supplies a link to the GCP Console page, allowing you to monitor the workload. Note,  that you can also monitor the workload using standard `kubectl` commands.

The last few lines printed by the command should look like that:

```
[XPK] Task: `Upload Docker Image` terminated with code `0`
[XPK] Task: `Creating Workload` is implemented by `kubectl apply -f /tmp/tmpvxwfhxbm`, streaming output live.
[XPK] Waiting for `Creating Workload`, for 0 seconds
jobset.jobset.x-k8s.io/test-workload-1 created
[XPK] Task: `Creating Workload` terminated with code `0`
[XPK] Follow your workload here: https://console.cloud.google.com/kubernetes/service/us-central2/gke-ml-cluster/default/test-workload-1/details?project=xxxx
[XPK] Exiting XPK cleanly
```

To delete the smoke test workload execute:

```bash
xpk workload delete \
--workload <WORKLOAD_ID> \
--cluster <CLUSTER_NAME> 
```

## Running sharding experiments

In this section we provide instructions for running parallelism experiments similar to the `tpu_hello_world` examples in the `jobset` [section](../jobset/README.md#example-1-tpu-hello-world-examples).

### Single slice ICI FSDP

To run a configuration for a single slice workload with Interchip Interconnect (ICI) sharding using Fully Sharded Data Parallelism (FSDP), follow the steps below:

- Create a workload script. Make sure to modify the `--ici_fsdp_parallelism` parameter to match your TPU type. The example `--ici_fsdp_parallelism=8` is configured for a TPU slice with 8 chips. E.g. v4-16 or v5p-16

```bash
cat <<EOF >./ici-fsdp.sh
#!/bin/bash
set -e

python3 pedagogical_examples/shardings.py --ici_fsdp_parallelism=8 --batch_size=131072 --embedding_dimension=2048

EOF
```

- Submit a workload

```bash

xpk workload create \
--workload <WORKLOAD_ID> \
--base-docker-image <MAX_TEXT_IMAGE_URI> \
--cluster <CLUSTER_NAME> \
--tpu-type <TPU_TYPE>  \
--num-slices 1 \
--command "bash ici-fsdp.sh" 
```

- To delete the workload execute:

```bash
xpk workload delete \
--workload <WORKLOAD_ID> \
--cluster <CLUSTER_NAME> 
```

### Multislice DCN DP and ICI FSDP

The below examples shows configuration for a multislice workload with data parallelism (DP) over data-center network (DCN) connections and FSDP over ICI.

- Create a workload script. Make sure to modify the `--ici_fsdp_parallelism` parameter to match your TPU type. The example `--ici_fsdp_parallelism=8` is configured for a TPU slice with 8 chips. E.g. v4-16 or v5p-16

```bash
cat <<EOF >./dcn-dp-ici-fsdp.sh
#!/bin/bash
set -e

python3 pedagogical_examples/shardings.py --dcn_data_parallelism=2 --ici_fsdp_parallelism=8 --batch_size=131072 --embedding_dimension=2048

EOF
```

- Submit a workload

```bash
xpk workload create \
--workload <WORKLOAD_ID> \
--base-docker-image <MAX_TEXT_IMAGE_URI> \
--cluster <CLUSTER_NAME> \
--tpu-type <TPU_TYPE>  \
--num-slices 2 \
--command "bash dcn-dp-ici-fsdp.sh" 
```

- To delete the workload execute:

```bash
xpk workload delete \
--workload <WORKLOAD_ID> \
--cluster <CLUSTER_NAME> 
```

## Running MaxText pretraining workloads

In this section we provide instructions for running MaxText pretraining for a 6.5B parameters model using the same configuration settings as in the [`examples\jobset\maxtext`](../jobset/README.md#example-2-maxtext-pre-training-examples).

### Single slice pretraining

- Create a workload script. 

> [!IMPORTANT]
> Before executing the below command, replace the ,`<RUN_NAME>`, `<DATASET_PATH>`, `<BASE_OUTPUT_DIRECTORY>` placeholders with values reflecting your environment. Refer to the instructions for [JobSet Maxtext examples](../jobset/README.md#maxtext-pre-training) for more information on how to set these parameters.
> Also, update the `ici_fsdp_parallelism` parameter to the number of chips in your TPU type.

```bash
cat <<EOF >./single-slice-6b.sh
#!/bin/bash
set -e

export LIBTPU_INIT_ARGS="--xla_enable_async_all_gather=true TPU_MEGACORE=MEGACORE_DENSE"

python3 MaxText/train.py MaxText/configs/base.yml \
run_name=<RUN_NAME> \
dataset_path=<DATASET_PATH> \
base_output_directory=<BASE_OUTPUT_DIRECTORY> \
steps=200 log_period=50 save_period=100 \
per_device_batch_size=16 \
dcn_data_parallelism=1 ici_fsdp_parallelism=8 \
remat_policy=full \
base_emb_dim=4096 base_num_heads=16 base_mlp_dim=16384 head_dim=256 base_num_decoder_layers=32

EOF
```

- Submit a workload

```bash
xpk workload create \
--workload <WORKLOAD_ID> \
--base-docker-image <MAX_TEXT_IMAGE_URI> \
--cluster <CLUSTER_NAME> \
--tpu-type <TPU_TYPE>  \
--num-slices 1 \
--command "bash single-slice-6b.sh" 
```

- To delete the workload execute:

```bash
xpk workload delete \
--workload <WORKLOAD_ID> \
--cluster <CLUSTER_NAME> 
```

### Multislice pretraining

- Create a workload script. 

> [!IMPORTANT]
> Before executing the below command, replace the ,`<RUN_NAME>`, `<DATASET_PATH>`, `<BASE_OUTPUT_DIRECTORY>` placeholders with values reflecting your environment. Refer to the instructions for [JobSet Maxtext examples](../jobset/README.md#maxtext-pre-training) for more information on how to set these parameters.
> Also, update the `ici_fsdp_parallelism` parameter to the number of chips in your TPU type.

```bash
cat <<EOF >./multi-slice-6b.sh
#!/bin/bash
set -e

export LIBTPU_INIT_ARGS="--xla_enable_async_all_gather=true TPU_MEGACORE=MEGACORE_DENSE"

python3 MaxText/train.py MaxText/configs/base.yml \
run_name=<RUN_NAME>  \
dataset_path=<DATASET_PATH>  \
base_output_directory=<BASE_OUTPUT_DIRECTORY> \
steps=200 log_period=50 save_period=100 \
per_device_batch_size=16 \
dcn_data_parallelism=2 ici_fsdp_parallelism=8 \
remat_policy=full \
base_emb_dim=4096 base_num_heads=16 base_mlp_dim=16384 head_dim=256 base_num_decoder_layers=32

EOF
```

- Submit a workload

```bash
xpk workload create \
--workload <WORKLOAD_ID> \
--base-docker-image <MAX_TEXT_IMAGE_URI> \
--cluster <CLUSTER_NAME> \
--tpu-type <TPU_TYPE>  \
--num-slices 2 \
--command "bash multi-slice-6b.sh" 
```

- To delete the workload execute:

```bash
xpk workload delete \
--workload <WORKLOAD_ID> \
--cluster <CLUSTER_NAME> 
```