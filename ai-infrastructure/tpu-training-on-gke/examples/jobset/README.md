# Examples using Jobset APIs

There are two set of examples in this folder showing how to configure and run training workloads with **JobSet** and **Kueue** APIs.

- [`TPU Hello World`](tpu_hello_world/) shows examples of experimenting with different data and model parallelism strategies  in single slice and multislice TPU configurations.
- The [MaxText](maxtext/) section provides examples of both single-slice and multi-slice pre-training for a MaxText model with 6.5 billion parameters.

We utilize [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) to streamline the customization of JobSet resource YAML definitions. 

The [base_jobset](base_jobset) folder houses a [Kustomize base](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/#bases-and-overlays) for JobSet configurations. The [tpu_hello_world](tpu_hello_world/) and [maxtext](maxtext/) folders contain [Kustomize overlays](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/#bases-and-overlays) that adapt the base configuration for use with the TPU Hello World and MaxText examples, respectively.

## TPU Hello World 

In the [`tpu_hello_world`](tpu_hello_world/) folder you will find examples of experimenting with different data and model parallelism strategies. The examples use the [`shardings.py`](https://github.com/google/maxtext/blob/main/pedagogical_examples/shardings.py) script from MaxText that is designed to make experimentation with different parallelism options easy for both single slice and multislice settings. For more information about parallelism strategies and TPU Multislice refer to the [Cloud TPU Multislice Overview](https://cloud.google.com/tpu/docs/multislice-introduction) article. 

### Configure the job

Set the current folder to [`tpu_hello_world`](tpu_hello_world/)

```
cd <REPO_ROOT_DIR>/ai-infrastructure/tpu-training-on-gke/examples/jobset/tpu_hello_world
```

Replace `<REPO_ROOT_DIR>` with the full path to the root of the cloned repo.


#### Update namespace, images, and job suffix

Remember to update the values in the kustomization.yaml file to align with your specific environment.

Set the namespace:

```
kustomize edit set namespace <NAMESPACE>
```

Replace `<NAMESPACE>` with the name of the Kubernetes namespace that was created during the setup, where the Kueue local queue has been provisioned. 

Set the Maxtext container image:

```
kustomize edit set image python=<ARTIFACT_REGISTRY_PATH>/maxtext-runner:latest
```

Replace `<ARTIFACT_REGISTRY_PATH>` with the path to your Artifact Registry.


Set the job ID suffix: 

```
kustomize edit set namesuffix -- <NAME_SUFFIX>
```

Replace `<NAME_SUFFIX>` with the suffix that will be appended to the default job name, which is `tpu-helloworld`. You can utilize the name suffix to prevent naming conflicts between concurrent jobs or to maintain completed jobs for tracking purposes.


#### Configure job topology and `shardings.py` parameters

Create the `parameters.env` file with the following key-value settings:

```
TPU_SLICE_TYPE=<TPU_SLICE_TYPE> 
TPU_TOPOLOGY=<TPU_TOPOLOGY> 
LOCAL_QUEUE=<LOCAL_QUEUE_NAME>
ICI_PARALLELISM=<ICI_PARALLELISM>
JOB_PARALLELISM=<JOB_PARALLELISM> 
NUM_SLICE=<NUM_SLICES>
```

Replace the following values:
- `<TPU_SLICE_TYPE>` and `<TPU_TOPOLOGY>` with the type and topology of a TPU slice you want to run your job on. For TPU v4, use `tpu-v4-podslice` for `<TPU_SLICE_TYPE>`. For TPU v5e, use `tpu-v5-lite-podslice`. For TPU v5p, use `tpu-v5p-slice`. For TPU v4, define the topology in 3-tuples, for example `2x2x2`. For TPU v5e, define the topology in 2-tuples. For TPU v5p, define the topology in 3-tuples. Refer to [TPU on GKE documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/tpus) for detailed information on TPU configurations.
- `<LOCAL_QUEUE_NAME>` with the name of the Kueue local queue in your namespace. Recall that the default name as created during the setup is `tpu-job-queue`
- `<ICI_PARALLELISM>` with the value that is equal to the number of chips in the TPU slice 
- `<JOB_PARALLELISM>` with the value that matches the number of TPU VMs in the TPU slice
- `<NUM_SLICES>` with the number of TPU slices on which you want to run the training job. Make sure to have at least this number of TPU node pools in your environment.

For your convenience, we have supplied two template files:

- `parameters.env.single_slice` with example settings tailored for a single slice job on a TPU v4-16 slice.
- `parameters.env.multi_slice` with example settings configured for a multi-slice job spanning two TPU v4-16 slices.


### Run the job

```bash
kubectl apply -k . 
```

#### Monitor jobs

You can review execution logs using [GKE Console](https://console.cloud.google.com/kubernetes/workload/overview) or from the command line using `kubectl`.

- To get the Kueue workloads:
```bash
kubectl get workloads -n <NAMESPACE>
```

- To get the JobSets:
```bash
kubectl get jobsets -n <NAMESPACE>
```

- To get pods in your namespace, including pods started by your workload:
```bash
kubectl get pods -n <NAMESPACE>
```

> [!NOTE]
> If your workload failed than the above command will not return the workload's pods as the JobSet operator cleans up all failed jobs. If you want to review logs from the failed workload use [GKE Console](https://console.cloud.google.com/kubernetes/workload/overview).

- To display logs for a pod:
```bash
kubectl logs -f -n <NAMESPACE> <YOUR POD>
```

Once the job is completed successfully, you will see a message similar to the following:
```
average time: 0.4840158, timings (seconds) [0.484098, 0.483838, 0.484114, 0.484056, 0.483973]
time is 0.4840158 seconds, TFLOP is 105.553116266496, TFLOP/s is 218.07783189411586
```

- To remove your workload and all resources that it created execute:
```bash
kubectl delete -k .
```



## MaxText pre-training 

The [`maxtext`](maxtext/) folder contains examples of pre-training a MaxText 6.5 billion parameters model on the [English C4 dataset](https://www.tensorflow.org/datasets/catalog/c4#c4en_default_config).

The [`maxtext/base_maxtext`](maxtext/base_maxtext/) folder contains the base configuration of the JobSet workload. In the [`maxtext/base_maxtext/jobset-spec-patch.yaml`](maxtext/base_maxtext/jobset-spec-patch.yaml) you will notice that a JobSet resource is configured with two job templates. One (named `slice`) starts the MaxText trainer and the other (named `tensorboard`) starts the TensorBoard uploader. The runtime parameters to the MaxText trainer and the TensorBoard uploader are passed through environment variables that are set through the `maxtext-parameters` ConfigMap.

The [`maxtext-6B`](maxtext/maxtext-6B/) folder contains the Kustomize overlay that customize the base MaxText JobSet configuration for running single slice and multislice training workloads.

### Configure the training job

Set the current folder to [`maxtext/maxtext-6B`](maxtext/maxtext-6B)

```
cd <REPO_ROOT_DIR>/ai-infrastructure/tpu-training-on-gke/examples/jobset/maxtext/maxtext-6B
```

Replace `<REPO_ROOT_DIR>` with the full path to the root of the cloned repo.

Set the namespace:

```
kustomize edit set namespace <NAMESPACE>
```

Replace `<NAMESPACE>` with the name of the Kubernetes namespace that was created during the setup, where the Kueue local queue has been provisioned. 

Set the Maxtext container image:

```
kustomize edit set image maxtext-runner-image=<ARTIFACT_REGISTRY_PATH>/maxtext-runner:latest
```

Set the TP Uploader container image

```
kustomize edit set image tb-uploader-image=<ARTIFACT_REGISTRY_PATH>/tb-uploader:latest
```


Replace `<ARTIFACT_REGISTRY_PATH>` with the path to your Artifact Registry.


Set the job ID suffix:

```
kustomize edit set namesuffix -- <NAME_SUFFIX>
```

Replace `<NAME_SUFFIX>` with the suffix that will be appended to the default job name, which is `maxtext-run`. You can utilize the name suffix to prevent naming conflicts between concurrent jobs or to maintain completed jobs for tracking purposes.


Set the job parameters: 

```
kustomize edit set configmap maxtext-parameters \
--from-literal=TPU_SLICE_TYPE=<TPU_SLICE_TYPE> \
--from-literal=TPU_TOPOLOGY=<TPU_TOPOLOGY> \
--from-literal=LOCAL_QUEUE=<LOCAL_QUEUE_NAME> \
--from-literal=ICI_PARALLELISM=<ICI_PARALLELISM> \
--from-literal=JOB_PARALLELISM=<JOB_PARALLELISM> \
--from-literal=NUM_SLICES=<NUM_SLICES> \
--from-literal=BASE_OUTPUT_DIRECTORY=<BASE_OUTPUT_DIRECTORY> \
--from-literal=RUN_NAME=<RUN_NAME> \
--from-literal=TENSORBOARD_NAME=<TENSORBOARD_NAME> \
--from-literal=DATASET_PATH=<DATASET_PATH> \
--from-literal=ARGS=<ARGS> \
--from-literal=LIBTPU_INIT_ARGS=<LIBTPU_INIT_ARGS>

```

Replace the following values:
- `<TPU_SLICE_TYPE>` and `<TPU_TOPOLOGY>` with the type and topology of a TPU slice you want to run your job on. For TPU v4, use `tpu-v4-podslice` for `<TPU_SLICE_TYPE>`. For TPU v5e, use `tpu-v5-lite-podslice`. For TPU v5p, use `tpu-v5p-slice`. For TPU v4, define the topology in 3-tuples, for example `2x2x2`. For TPU v5e, define the topology in 2-tuples. For TPU v5p, define the topology in 3-tuples. Refer to [TPU on GKE documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/tpus) for detailed information on TPU configurations.
- `<LOCAL_QUEUE_NAME>` with the name of the Kueue local queue in your namespace. Recall that the default name as created during the setup is `tpu-job-queue`
- `<ICI_PARALLELISM>` with the value that is equal to the number of chips in the TPU slice 
- `<JOB_PARALLELISM>` with the value that matches the number of TPU VMs in the TPU slice
- `<NUM_SLICES>` with the number of TPU slices on which you want to run the training job. Make sure to have at least this number of TPU node pools in your environment.
- `<BASE_OUTPUT_DIRECTORY>` with the Cloud Storage location for checkpoints and logs. 
- `<DATASET_PATH>` with the Cloud Storage location of the C4 dataset. Specify the Cloud Storage location of the C4 dataset, excluding the `c4` folder name in the path. As part of the setup for the examples' prerequisites, the C4 dataset is copied to the `gs://<ARTIFACT_BUCKET>/datasets/c4` location.
- `<RUN_NAME>` with the MaxText run name. MaxText will use this value to name the folders for checkpoints and TensorBoard logs in the `<BASE_OUTPUT_DIRECTORY>`. If you want to restart from a previously set checkpoint set this to the run name used for the previous run. Although not required it may be convenient to use the same name as the `<NAME_SUFFIX>`.
- `<TENSORBOARD_NAME>` with the fully qualified name of the TensorBoardr instance to use for a training run tracking. The format should be - `projects/<PROJECT_NUMBER>/locations/<TENSORBOARD_REGION>/tensorboard/<TENSORBOARD_ID>`. If you provisioned your environment using the automated setup, you can retrieve the TensorBoard name from the Terraform state, using the `terraform output tensorboard_id` command.
- `<ARGS>` with any additional parameters you want to pass to the MaxText trainer. Refer to the below notes and the [MaxText documentation](https://github.com/google/maxtext/blob/main/MaxText/configs/base.yml) for more info.
- `<LIBTPU_INIT_ARGS>` with `libtpu` and XLA compiler settings. Refer to the below notes and the [MaxText documentation](https://github.com/google/maxtext/tree/main) for more info

The MaxText trainer [`MaxText/train.py`](https://github.com/google/maxtext/blob/main/MaxText/train.py) accepts a number of command line parameters that define a training regimen and model architecture. The required parameters are `run_name`, `base_output_directory`, and `dataset_path`. Other parameters are optional with the default values set in the [MaxText config file](https://github.com/google/maxtext/blob/main/MaxText/configs/base.yml). 

The required parameters are set through the `RUN_NAME`, `BASE_OUTPUT_DIRECTORY`, and `DATASET_PATH` fields and the optional ones through the `ARGS` field in the `maxtext-parameters` *configMap* as described above. 

For both single slice and multislice job types, you can utilize the `ARGS` field to configure training regimen parameters, such as training steps, batch size, ICI (Inter-Chunk Interaction) settings, DCN (Deep Cascade Network) parallelization settings, and parameters that control the model architecture.

Below are example settings for a pretraining task of a ~6.5B parameter model. These settings have been thoroughly tested to achieve high model flops utilization (MFU) on v4-16 slices. We encourage you to experiment with your own settings as well.

#### Settings for a single slice job

These are sample settings for a single slice job on a v4-32 slice.

```
ARGS="steps=200 log_period=50 save_period=100 dcn_data_parallelism=1 ici_fsdp_parallelism=16 per_device_batch_size=16 remat_policy=full base_emb_dim=4096 base_num_heads=16 base_mlp_dim=16384 head_dim=256 base_num_decoder_layers=32" 
```

```
LIBTPU_INIT_ARGS="--xla_enable_async_all_gather=true TPU_MEGACORE=MEGACORE_DENSE"
```

This is a sample command that configures a single slice job

```
kustomize edit set configmap maxtext-parameters \
--from-literal=TPU_SLICE_TYPE=tpu-v4-podslice \
--from-literal=TPU_TOPOLOGY=2x2x2 \
--from-literal=LOCAL_QUEUE=tpu-job-queue \
--from-literal=ICI_PARALLELISM=8 \
--from-literal=JOB_PARALLELISM=2 \
--from-literal=NUM_SLICES=1 \
--from-literal=BASE_OUTPUT_DIRECTORY=gs://jk2-artifact-repository \
--from-literal=RUN_NAME=single-slice-101 \
--from-literal=TENSORBOARD_NAME=projects/895222332033/locations/us-central1/tensorboards/9108042063194095616 \
--from-literal=DATASET_PATH=gs://jk2-artifact-repository/datasets \
--from-literal=ARGS="steps=200 log_period=50 save_period=100 dcn_data_parallelism=2 ici_fsdp_parallelism=16 per_device_batch_size=16 remat_policy=full base_emb_dim=4096 base_num_heads=16 base_mlp_dim=16384 head_dim=256 base_num_decoder_layers=32" \
--from-literal=LIBTPU_INIT_ARGS="--xla_enable_async_all_gather=true TPU_MEGACORE=MEGACORE_DENSE"
```

#### Settings for a multi-slice job 

These are sample settings for a single slice job on a v4-32 slice.

```
ARGS="steps=200 log_period=50 save_period=100 dcn_data_parallelism=2 ici_fsdp_parallelism=16 per_device_batch_size=16 remat_policy=full base_emb_dim=4096 base_num_heads=16 base_mlp_dim=16384 head_dim=256 base_num_decoder_layers=32" 
```

```
LIBTPU_INIT_ARGS="--xla_enable_async_all_gather=true TPU_MEGACORE=MEGACORE_DENSE"
```







 


#### Run the job

```bash
kubectl apply -k . 

### Configure the job

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