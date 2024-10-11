# TPU training workloads examples

Before continuing with this guide, ensure you have provisioned the training environment as outlined in the [environment setup](../README.md#provision-infrastructure). In this reference guide  we recommend using the **JobSet** and **Kueue** APIs as the preferred way to orchestrate large-scale distributed training workloads on GKE. You can create JobSet yaml configurations in a variety of ways. Our examples demonstrate two approaches:
- Using [Kustomize](https://kustomize.io/). **Kustomize** is a tool that streamlines and simplifies the creation and adaptation of complex configurations like JobSets. It provides robust configuration management and template-free customization. The examples of creating JobSet configurations using Kustomize are in the [jobset](jobset/) folder.
- Using [xpk](https://github.com/google/maxtext/tree/main/xpk). **xpk** (Accelerated Processing Kit) is a Python-based tool that helps to orchestrate large-scale training jobs on GKE. **xpk** provides a simple command-line interface for managing GKE clusters and submitting training workloads that are encapsulated as JobSet configurations. In this reference guide, we do not use cluster management capabilities. We use **xpk** to configure and submit training workloads to the GKE-based training environment provisioned during the setup. The **xpk** examples are in the [xpk](xpk/) folder.

The examples are all based on the [MaxText](https://github.com/google/maxtext/tree/main) code base. MaxText is a high-performance, highly scalable, open-source LLM code base written in pure Python/Jax. It is optimized for Google Cloud TPUs and can achieve 55% to 60% MFU (model flops utilization). MaxText is designed to be a launching point for ambitious LLM projects in both research and production. It is also an excellent code base for demonstrating large-scale training design and operational patterns as attempted in this guide.

## Prerequisites for running examples

### Build the MaxText container image and download training datasets

Before you can run the examples, you need to package MaxText in a training container image. You also need to copy the datasets required by the samples to your Cloud Storage  artifact repository. We have automated this process with Cloud Build. 

NOTE: Ensure you are working from  the `examples` directory

```bash
export PROJECT_ID=<PROJECT_ID>
export ARTIFACT_BUCKET=gs://<ARTIFACT_BUCKET>
export ARTIFACT_REGISTRY_PATH=<ARTIFACT_REGISTRY_PATH>
export AUTOMATION_ACCOUNT=<AUTOMATION_SERVICE_ACCOUNT>
export JAX_VERSION=NONE
export MODE=stable

gcloud builds submit \
  --project $PROJECT_ID \
  --config build-images-datasets.yaml \
  --substitutions _ARTIFACT_BUCKET=$ARTIFACT_BUCKET,_ARTIFACT_REGISTRY_PATH=$ARTIFACT_REGISTRY_PATH,_AUTOMATION_ACCOUNT=$AUTOMATION_ACCOUNT,_JAX_VERSION=$JAX_VERSION,_MODE=$MODE \
  --machine-type=e2-highcpu-32 \
  --quiet
```

Replace the following values:
- `<PROJECT_ID>` - your project ID.
- `<ARTIFACT_BUCKET>` - the name of the Google Cloud Storage (GCS) bucket where you want to manage training artifacts like datasets and checkpoints. Recall that if you haven't made any changes to the defaults during the environment setup, the name should be `<YOUR_PREFIX>-artifact-repository`.
- `<ARTIFACT_REGISTRY_PATH>` - the path to the Artifact Registry that you intend to use for pushing the Maxtext  container image. Keep in mind that the default path, as established during the setup process, is `us-docker.pkg.dev/<YOUR_PROJECT_ID>/<YOUR_PREFIX>-training-images`. If you made any modifications to these defaults, please make the necessary updates  accordingly.
- `<AUTOMATION_SERVICE_ACCOUNT>` - your automation service account. Refer to the environment setup section.
- By default, the MaxText image will be built with the default version of Jax. If you want to use a specific version, modifyt the `JAX_VERSION` setting.

### Set up your development environment

Before you can run the examples, it's necessary to install the latest versions of [Kustomize](https://kustomize.io/) and [xpk](https://github.com/google/xpk) on your development workstation.


- To install Kustomize, please follow the instructions in the [Kustomize documentation](https://kubectl.docs.kubernetes.io/installation/kustomize/binaries/). 

- To install [xpk](https://github.com/google/xpk)

```
pip install xpk
```

You also need to set credentials to your GKE cluster.
```
gcloud container clusters get-credentials <CLUSTER_NAME> --region <CLUSTER_REGION>
```

Replace `<CLUSTER_NAME>` and `<CLUSTER_REGION>` to match your environment.


> [!NOTE]
> You may be prompted to to install the `gke-gcloud-auth-plugin` binary to use kubectl with the cluser. Run `gcloud components install gke-gcloud-auth-plugin` to install the plugin.

## Running examples

For detailed instructions on running specific examples refer to README documents in the [`jobset`](./jobset) and [`xpk`](./xpk) folders.


