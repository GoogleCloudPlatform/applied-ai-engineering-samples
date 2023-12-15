# Deploy and load test  Llama-2 7B model

This walkthrough shows you how to deploy and load test Llama-2 7B model. 


## Download the Llama-2 7B checkpoint

Follow the instructions on [Llama 2 repo](https://github.com/facebookresearch/llama/blob/main/README.md) to access Llama 2 checkpoints. Download the checkpoints to a GCS location.


## Convert the checkpoint

Before deploying the model to Saxml, you need to convert the original Meta checkpoints to the format required by Saxml by running a checkpoint converter job.

### Configure a converter job

Set the NAMESPACE environment variable to the Saxml workload namespace in your cluster.  You can retrieve the namespace name by executing `terraform output namespace` from the `environment\1-base_environment` folder.

Set the ARTIFACT_REGISTRY variable to your Artifact Registry path. If you created an Artifact Registry during the base environment setup you can retrieve the path by executing `terraform output artifact_registry_image_path` from the `environment\1-base_environment` folder

From the `checkpoint_converter/manifests` folder:

```
ARTIFACT_REGISTRY="your-artifact-registry-path"
NAMESPACE="your-namespace"
CHECKPOINT_CONVERTER_IMAGE_URI="$ARTIFACT_REGISTRY/checkpoint-converter:latest"

kustomize edit set namespace $NAMESPACE
kustomize edit set image checkpoint-converter=$CHECKPOINT_CONVERTER_IMAGE_URI
```

Update the  `parameters.env`  file as follows:
- Set `GCS_BASE_CHECKPOINT_PATH` to the GCS location of the Llama-2-7b checkpoint you downloaded in the previous step
- Set `GCS_PAX_CHECKPOINT_PATH` to the GCS location where you want to store the converted checkpoint.  
- Set `KSA` to the Kubernetes service account name configured for Workload Identity. You can retrieve the name by executing the `terraform output ksa_name` command from the `environment/1-base_environment` folder.
- Do not modify the `ARGS` and `CHECKPOINT_FOLDER_NAME` parameters

### Start the conversion job:

```
kubectl apply -k . 
```

You can monitor the progress of the job using **Cloud Console** or by streaming logs with `kubectl logs` command.

## Deploy the model

You will use the `saxutil` command-line utility to deploy the model. A Kubernetes Deployment hosting `saxutil` was created when you deployed **Saxml** to the cluster. To use the utility, execute a shell in the deployment's pod.

List the pods.

```
kubectl get pods -n "your-namespace"
```

The pod hosting `saxutil` should have a name starting with the `saxml-util` prefix.

Open a shell in the pod.

```
kubectl exec -it "your-pod-name" -n "your-namespace"  -- /bin/bash
```
