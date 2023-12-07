# Examples using Jobset APIs

There are two set of examples in this folder showing how to configure and run training workloads with **JobSet** and **Kueue** APIs using **Kustomize**.

- [`TPU Hello World`](tpu_hello_world/) shows examples of experimenting with different data and model parallelism strategies with in single slice and multislice TPU configurations.
- [`MaxText`](maxtext/) shows examples of pre-training a MaxText 6.5B parameter model in both single slice and multislice TPU configurations.

## Configuring and running JobSet workloads with Kustomize

The examples in this folder show how to configure and run JobSet workloads using Kustomize. The [`base_jobset`](base_jobset) folder contains the base JobSet configuration that is referenced in overlays in the `tpu_hello_world` and `maxtext` folders.

> [!IMPORTANT]
> Before running the examples, modify the [`base_jobset/jobset.yaml`](jobset/base_jobset/jobset.yaml) file to reflect the topology of TPU slices provisioned in your environment. 
> For example, if you provisioned `v4-64` based node pools:
> - Update the node selector settings in  `spec.replicatedJobs.template.spec.template.spec.nodeSelector` with `tpu-v4-podslice` and `2x4x4` values and 
> - Update the `parallelism` and `completions` fields in the `spec.replicatedJobs.template.spec` with 4 - a v4-64 slice comprises 4 TPU VMs. 
> You can refer to the [table](../../main/README.md#input-variables-in-the-terraform-configuration) in Terraform configuration for TPU slice configuration. 


## EXAMPLE 1. TPU Hello World examples

In the [`tpu_hello_world`](tpu_hello_world/) folder you will find examples of experimenting with different data and model parallelism strategies. The examples use the [`shardings.py`](https://github.com/google/maxtext/blob/main/pedagogical_examples/shardings.py) script from MaxText that is designed to make experimentation with different parallelism options easy for both single slice and multislice settings. For more information about parallelism strategies and TPU Multislice refer to the [Cloud TPU Multislice Overview](https://cloud.google.com/tpu/docs/multislice-introduction) article. There are two example configurations:

- The [`tpu_hello_world/single_slice`](tpu_hello_world/single_slice) folder contains the example configuration of a single slice workload configured for  Interchip Interconnect (ICI) sharding using Fully Sharded Data Parallelism (FSDP). 
- The [`tpu_hello_world/multi-slice`](tpu_hello_world/multi-slice) is a configuration for a multislice workload with data parallelism (DP) over data-center network (DCN) connections and FSDP over ICI.

### Configure jobs

We use `envsubst` tool to adapt the examples to your environment the `namespace` and `images` fields in the `kustomization.template.yaml` files to reference names used in your configuration. 
- `namespace` field refers to the Kubernetes namespace created during setup (`$NAMESPACE` in [`vars.env`](../../env_setup/vars.env))
- As your recall, a Kueue LocalQueue used to admit workloads has been provisioned in this namespace. The `newName` property of the `images` field with the name of your MaxText training container image (`$MAX_TEXT_IMAGE_NAME` in [`examples.env`](../examples.env)).

### Run jobs

Run the following commands to set the environment variables you have used for configuration during provisioning:

```bash
export REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
source ${REPO_ROOT_DIR}/env_setup/vars.env
source ${REPO_ROOT_DIR}/examples/examples.env
pushd ${REPO_ROOT_DIR}/examples/jobset/tpu_hello_world
```

To run a single slice example execute the following command from the [`tpu_hello_world`](tpu_hello_world) folder:

```bash
envsubst < single_slice/kustomization.template.yaml > single_slice/kustomization.yaml
kubectl apply -k single_slice
```

To run a Multislice sample execute the following command from the [`tpu_hello_world`](tpu_hello_world) folder:

```bash
envsubst < multi_slice/kustomization.template.yaml > multi_slice/kustomization.yaml
kubectl apply -k multi_slice
```

Note that the multi-slice example is configured to run on two slices so you need at least two multi-host TPU node pools in your environment to execute it successfully.

### Monitor jobs

You can review execution logs using [GKE Console](https://console.cloud.google.com/kubernetes/workload/overview) or from the command line using `kubectl`.

- To get the Kueue workloads:
```bash
kubectl get workloads -n $NAMESPACE
```

- To get the JobSets:
```bash
kubectl get jobsets -n $NAMESPACE
```

- To get pods in your namespace, including pods started by your workload:
```bash
kubectl get pods -n $NAMESPACE
```

> [!NOTE]
> If your workload failed than the above command will not return the workload's pods as the JobSet operator cleans up all failed jobs. If you want to review logs from the failed workload use [GKE Console](https://console.cloud.google.com/kubernetes/workload/overview).

- To display logs for a pod:
```bash
kubectl logs -f -n $NAMESPACE <YOUR POD>
```

Once the job is completed successfully, you will see a message similar to the following:
```
average time: 0.4840158, timings (seconds) [0.484098, 0.483838, 0.484114, 0.484056, 0.483973]
time is 0.4840158 seconds, TFLOP is 105.553116266496, TFLOP/s is 218.07783189411586
```

- To remove your workload and all resources that it created execute:
```bash
kubectl delete -n $NAMESPACE -k single_slice
```
or
```bash
kubectl delete -n $NAMESPACE -k multi_slice
```

## EXAMPLE 2. MaxText pre-training examples

The [`maxtext`](maxtext/) folder contains examples of pre-training a MaxText 6.5 billion parameters model on the [English C4 dataset](https://www.tensorflow.org/datasets/catalog/c4#c4en_default_config), downloaded as part of [prerequisites](../README.md#prerequisites-for-running-examples) to running examples.

The [`maxtext/base_maxtext`](maxtext/base_maxtext/) folder contains the base configuration of the JobSet workload. In the [`maxtext/base_maxtext/jobset-spec-patch.yaml`](maxtext/base_maxtext/jobset-spec-patch.yaml) you will notice that a JobSet resource is configured with two job templates. One (named `slice`) starts the MaxText trainer and the other (named `tensorboard`) starts the TensorBoard uploader. The runtime parameters to the MaxText trainer and the TensorBoard uploader are passed through environment variables that are set through the `maxtext-parameters` ConfigMap.

The [`single-slice-6B`](maxtext/single-slice-6B/) and [`multi-slice-6B`](maxtext/multi-slice-6B/) folders contain the Kustomize overlays that customize the base MaxText JobSet configuration for running a single slice and multislice training workloads respectively.

### Configure jobs

You will use `envsubst` tool to adapt the examples to your environment (using environment variables) and update `single-slice-6B\kustomization.template.yaml` and `multi-slice-6B\kustomization.template.yaml` files to reference names used in your configuration. Following are the fields for configuration:

- `namespace` refers to the Kubernetes namespace created during setup (`$NAMESPACE` in [`vars.env`](../../env_setup/vars.env))
- `newName` property of the `images` field refers to the name of your MaxText training container image (`$MAX_TEXT_IMAGE_NAME` in [`examples.env`](../examples.env)).
- `nameSuffix` field refers to with a unique identifier of your workload. If you try to submit a workload using the same identifier as in any of the previous workloads you will receive an error. You will configure `$MAXTEXT_JOB_ID` in the following command. For example, `singleslice-6b-105`.
- Fields in the `configMapGenerator` 
  - `REPLICAS` - The number of TPU slices to use for the job. If set to a number higher than 1 a multi-slice job will be started
  - `RUN_NAME` - The MaxText run name. MaxText will use this value to name the folders for checkpoints and TensorBoard logs - see BASE_OUTPUT_DIRECTORY. If you want to restart from a previously set checkpoint set this to the run name used for the previous run. Although not required it may be convenient to use the same name as the `nameSuffix`.
  - `BASE_OUTPUT_DIRECTORY` - The base Cloud Storage location for checkpoints and logs.
  - `DATASET_PATH` - The base Cloud Storage location for the C4 dataset. Do not include the `c4` folder name. E.g. if the `c4` dataset was copied to `gs:\\bucket_name\datasets` set the DATASET_PATH to this URI. DATASET_PATH is set to `$DATASETS_URI` from [`examples.env`](../examples.env)
  - `TENSORBOARD_NAME`` - The full name of the TensorBoard instance you want to use for tracking. In the format `projects\YOUR_PROJECT_NUMBER\locations\YOUR_LOCATON\tensorboard\YOUR_TENSORBOARD_ID`. You can get the full name of TensorBoard from the Terraform state file as shown in the following command.
  - `ARGS` - Any additional parameters you want to pass to the MaxText trainer. Refer to the below notes and the [MaxText documentation](https://github.com/google/maxtext/blob/main/MaxText/configs/base.yml) for more info.
  - `LIBTPU_INIT_ARGS` - An environmental variable that controls `libtpu` including XLA compiler. Refer to [MaxText documentation](https://github.com/google/maxtext/tree/main) for more info.

The MaxText trainer [`MaxText/train.py`](https://github.com/google/maxtext/blob/main/MaxText/train.py) accepts a number of command line parameters that define a training regimen and model architecture. The required parameters are `run_name`, `base_output_directory`, and `dataset_path`. Other parameters are optional with the default values set in the [MaxText config file](https://github.com/google/maxtext/blob/main/MaxText/configs/base.yml). 

In our examples, the required parameters are set through the `RUN_NAME`, `BASE_OUTPUT_DIRECTORY`, and `DATASET_PATH` fields and the optional ones through the `ARGS` field in the `maxtext-parameters` *configMap* as described above. 

In both single slice and multislice examples, we use the `ARGS` field to set the training regimen parameters like training steps or batch size,  ICI and DCN parallelization settings, and parameters controlling model architecture for a ~6.5B parameter model pretraining task. These settings have been tested to achieve high model flops utilization (MFU). We encourage you to experiment with your own settings.

> [!IMPORTANT]
> Make sure that the `REPLICAS` field and the `dcn_data_parallelism` and `ici_fsdp_parallelism` trainer parameters align with the TPU topology configured in your environment.

### Run jobs

Run the following commands to set the environment variables you have used for configuration during provisioning:

```bash
export REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
source ${REPO_ROOT_DIR}/env_setup/vars.env
source ${REPO_ROOT_DIR}/examples/examples.env
pushd ${REPO_ROOT_DIR}/examples/jobset/maxtext
```

To run a single slice example execute the following command from the [`maxtext`](maxtext) folder:

```bash
export TENSORBOARD_ID=$(gsutil cat gs://${TF_STATE_BUCKET}/${TF_STATE_PREFIX}/default.tfstate | jq '.outputs.tensorboard_id.value')
export MAXTEXT_JOB_ID=YOUR_UNIQUE_JOB_ID
envsubst < single-slice-6B/kustomization.template.yaml > single-slice-6B/kustomization.yaml
kustomize build single-slice-6B | kubectl apply -f -
```

> [!NOTE]
> Note that we use `kustomize` utility as some of the **Kustomize** features we utilize are not yet supported by `kubectl`.

To start a multislice training example execute the following command from the [`maxtext`](maxtext) folder:

```bash
kustomize build multi-slice-6B | kubectl apply -f -
```

### Monitor jobs

You can monitor the runs using the techniques described in the [`tpu_hello_world`](#monitor-jobs) section. Since both single slice and multislice workloads  upload TensorBoard metrics generated by the MaxText trainer to Vertex AI TensorBoard, you can also monitor the run - in real time - through [Vertex Experiments](https://console.cloud.google.com/vertex-ai/experiments/experiments). The experiment name that will receive the metrics is the same as the value configured in `RUN_NAME`

- To remove your workload and all resources that it created execute:
```bash
kustomize build single-slice-6B | kubectl delete -n $NAMESPACE -f -
```
or
```bash
kustomize build multi-slice-6B | kubectl delete -n $NAMESPACE -f -
```