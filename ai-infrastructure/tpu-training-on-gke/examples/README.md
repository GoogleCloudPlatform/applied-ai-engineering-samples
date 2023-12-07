# TPU training workloads examples

Before continuing with this guide, ensure you have provisioned the training environment as outlined in the [README](../README.md#provision-infrastructure) of the repo. In this reference guide  we recommend using the **JobSet** and **Kueue** APIs as the preferred way to orchestrate large-scale distributed training workloads on GKE. You can create JobSet yaml configurations in a variety of ways. Our examples demonstrate two approaches:
- Using [Kustomize](https://kustomize.io/). **Kustomize** is a tool that streamlines and simplifies the creation and adaptation of complex configurations like JobSets. It provides robust configuration management and template-free customization. The examples of creating JobSet configurations using Kustomize are in the `jobset` folder.
- Using [xpk](https://github.com/google/maxtext/tree/main/xpk). **xpk** (Accelerated Processing Kit) is a Python-based tool that helps to orchestrate large-scale training jobs on GKE. **xpk** provides a simple command-line interface for managing GKE clusters and submitting training workloads that are encapsulated as JobSet configurations. In this reference guide, we do not use cluster management capabilities. We use **xpk** to configure and submit training workloads to the GKE-based training environment provisioned during the setup. The **xpk** examples are in the `xpk` folder.

The examples are all based on the [MaxText](https://github.com/google/maxtext/tree/main) code base. MaxText is a high-performance, highly scalable, open-source LLM code base written in pure Python/Jax. It is optimized for Google Cloud TPUs and can achieve 55% to 60% MFU (model flops utilization). MaxText is designed to be a launching point for ambitious LLM projects in both research and production. It is also an excellent code base for demonstrating large-scale training design and operational patterns as attempted in this guide.

## Prerequisites for running examples

### Building Training Container Image
Before you can run the examples, you need to package MaxText in a training container image. You also need to build auxiliary images used in some examples, including a container image that packages the [TensorBoard uploader](https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-overview#upload-tb-logs) and to copy the datasets required by the samples to your Cloud Storage data and artifact repository. We have automated this process with Cloud Build. 

Modify the settings in [`examples.env`](examples.env) file to reflect your environment and submit the build:

- `DATASETS_URI` - the location in Cloud Storage bucket where datasets are downloaded
- `MAX_TEXT_IMAGE_NAME` - the name of the container image packaging MaxText (MaxText scripts uploads container image to Container Registry in the project configured)
- `TB_UPLOADER_IMAGE_URI` - the full URI of the container image in Artifact Registry packaging TensorBoard uploader

NOTE: Ensure you are working from `examples` directory

```bash
export REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
pushd ${REPO_ROOT_DIR}/examples
source ${REPO_ROOT_DIR}/env_setup/vars.env
source ${REPO_ROOT_DIR}/examples/examples.env

gcloud builds submit \
  --project $PROJECT_ID \
  --config build-images-datasets.yaml \
  --substitutions _MAXTEXT_IMAGE_NAME=$MAX_TEXT_IMAGE_NAME,_TB_UPLOADER_IMAGE_URI=$TB_UPLOADER_IMAGE_URI,_DATASETS_URI=$DATASETS_URI \
  --machine-type=e2-highcpu-32 \
  --quiet
```


### Setting up development environment

Run the following steps in your development environment (e.g. Cloud Shell) before running the commands:

- To submit workloads to the cluster you need to create cluster credentials.

```
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION
```

> [!NOTE]
> You may be prompted to to install the `gke-gcloud-auth-plugin` binary to use kubectl with the cluser. Run `gcloud components install gke-gcloud-auth-plugin` to install the plugin.


- To install Kustomize, please follow the instructions in the [Kustomize documentation](https://kubectl.docs.kubernetes.io/installation/kustomize/). If you running from Cloud Shell, you can run the following commands to install Kustomize by downloading precompiled binaries.:

```bash
USER_HOME=$(bash -c "cd ~$(printf %q $USER) && pwd")
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash -s -- ${USER_HOME}
export PATH="${USER_HOME}:${PATH}"
```

- **xpk** is implemented as a [Python script](https://github.com/google/xpk/blob/main/xpk.py) and distributed through the [xpk repo](https://github.com/google/xpk). To access **xpk** you can either clone the whole repo or download the `xpk.py` module.


```bash
USER_HOME=$(bash -c "cd ~$(printf %q $USER) && pwd")
curl -s "https://raw.githubusercontent.com/google/xpk/main/xpk.py" --output ${USER_HOME}/xpk.py
chmod +x ${USER_HOME}/xpk.py
export PYTHONPATH="$USER_HOME:$PYTHON_PATH"
```


## Running examples

For detailed instructions on running specific examples refer to README documents in the [`jobset`](./jobset) and [`xpk`](./xpk) folders.


