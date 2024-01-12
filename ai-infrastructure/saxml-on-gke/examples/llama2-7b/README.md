# Deploy and load test  Llama-2 7B model

This walkthrough shows you how to deploy and load test the Llama-2 7B model. 


## Download the Llama-2 7B checkpoint

Follow the instructions on [Llama 2 repo](https://github.com/facebookresearch/llama/blob/main/README.md) to access Llama 2 checkpoints. Download the checkpoints to a GCS location.

## Convert the checkpoint

Before deploying the model to Saxml, you need to convert the original Meta checkpoints to the format required by Saxml by running a checkpoint converter job.

### Configure a converter job


From the [manifests](convert_checkpoint/manifests/) folder, execute the following steps:

Update the namespace in [kustomization.yaml](convert_checkpoint/manifests/kustomization.yaml).

```
kustomize edit set namespace <SAXML_NAMESPACE> 
```

Replace `<SAXML_NAMESPACE>` with the namespace for Saxml workloads, which  was created during the setup. 

Copy [parameters.env.tmpl](convert_checkpoint/manifests/parameters.env.tmpl) to `parameters.env`

Update  `parameters.env`  follows:
- Set `GCS_BASE_CHECKPOINT_PATH` to the GCS location of the Llama-2-7b checkpoint you downloaded in the previous step
- Set `GCS_PAX_CHECKPOINT_PATH` to the GCS location where you want to store the converted checkpoint.  
- Set `KSA` to the Kubernetes service account name configured for Workload Identity. 

### Start the conversion job:

```shell
skaffold run --default-repo <ARTIFACT_REGISTRY> --profile cloudbuild 
```

Replace `<ARTIFACT_REGISTRY>` with the path to your Artifact Registry. 


You can monitor the progress of the job using **Cloud Console** or by streaming logs with `kubectl logs` command.


## Deploy the model

You will use the `saxutil` command-line utility to deploy the model. A Kubernetes Deployment hosting `saxutil` was created when you deployed **Saxml** to the cluster. To use the utility, execute a shell in the deployment's pod.

List the pods.

```shell
kubectl get pods -n <SAXML_NAMESPACE> 
```

The pod hosting `saxutil` has a name starting with the `saxml-util` prefix. E.g.
```shell
NAME                                READY   STATUS    RESTARTS   AGE
saxml-util-d469c5b55-gs45w           1/1     Running   0          22h
```

Open a shell in the pod.

```shell
kubectl exec -it <SAXUTIL_POD> -n <SAXML_NAMESPACE>  -- /bin/bash
```

Several environment variables are pre-set in the `saxutil` pod, including `SAX_CELL` and `SAX_ROOT`, which are set to the name of the Saxml cell and the name of the Saxml root folder, respectively. You will use the predefined Llama-2 7B model configuration to deploy the checkpoint.


Execute the following commands to deploy the model:

```shell
saxutil publish \
${SAX_CELL}/llama7bfp16tpuv5e \
saxml.server.pax.lm.params.lm_cloud.LLaMA7BFP16TPUv5e \
<CHECKPOINT_PATH> \
1 \
BATCH_SIZE=[1]
```

Replace `<CHECKPOINT_PATH>` with the path to the converted checkpoint. Make sure to include the checkpoint folder in the path. For instance, if the checkpoint is located in the `checkpoint_00000000` folder within the `<GCS_PAX_CHECKPOINT_PATH>` path  `<CHECKPOINT_PATH>` should be `<GCS_PAX_CHECKPOINT_PATH>/checkpoint_00000000` 

The above command deploys as single replica of the model and configures the Saxml model server to use a batch size of 1.

Monitor the model server pod until the model loading is complete. This process may take some time.

```
kubectl logs <SAX_MODEL_SERVER_POD> -n <SAXML_NAMESPACE>
```

Wait until you see a similar message:

```
I1102 14:15:00.962680 134004674082368 servable_model.py:697] loading completed.
```

After the model is loaded, run a query to verify that the model is working.

```shell
saxutil lm.generate ${SAX_CELL}/llama7bfp16tpuv5e "Who is Harry Potter's mother?"
```

You should see a response similar to the following:
```
+--------------------------------+-----------+
|            GENERATE            |   SCORE   |
+--------------------------------+-----------+
|  Harry Potter's mother is Lily | -10.57283 |
| Evans. Who is Harry Potter's   |           |
| father? Harry Potter's father  |           |
| is                             |           |
+--------------------------------+-----------+
```



