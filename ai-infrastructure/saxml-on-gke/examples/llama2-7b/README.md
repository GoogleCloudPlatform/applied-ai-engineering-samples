# Deploying  Llama-2 7B model

*Work in progress*

## Download the GTPJ-6B checkpoint

Follow the instructions on [Llama 2 repo](https://github.com/facebookresearch/llama/blob/main/README.md) to access Llama 2 checkpoints. Download the checkpoints to a GCS location.


## Convert the checkpoint

Update the  `converter-parameters configMapGenerater` in  the `convert_checkpoint\kustomization.yaml` file as follows:
- Set `GCS_BASE_CHECKPOINT_PATH` to the GCS location of the GTPJ-6B checkpoint you downloaded in the previous step
- Set `GCS_PAX_CHECKPOINT_PATH` to the GCS location where you want to store the converted checkpoint. 
- Update `ARGS="--model-size=7b"` to specify the model size for the checkpoint to be converted

Start the conversion job:

```
kubectl apply -k convert_checkpoint
```

## Publish the model


List pods

```
kubectl get pods -n <YOUR NAMESPACE>
```

Execute shell on the server

```
kubectl exec -it <SAX UTIL POD> -n <YOUR NAMESPACE> -- /bin/bash
```

### Publish the model

#### Set parameters

```
CHECKPOINT_PATH=gs://CHECKPOINT_PATH
CHECKPOINT_PATH=gs://jk-saxml-model-repository/pax-llama-7b/checkpoint_00000000
SAX_ROOT=gs://SAX_ADMIN_BUCKET/sax-root
SAX_ROOT=gs://jk-saxml-admin-bucket/sax-root
SAX_CELL=/sax/test
MODEL_NAME=llama7bfp16tpuv5e
MODEL_CONFIG_PATH=saxml.server.pax.lm.params.lm_cloud.LLaMA7BFP16TPUv5e
REPLICA=1
```

#### List published models

```
saxutil ls $SAX_CELL

```

#### Publish model

```
saxutil  publish \
${SAX_CELL}/${MODEL_NAME} \
${MODEL_CONFIG_PATH} \
${CHECKPOINT_PATH} \
${REPLICA}
```

#### Publish model

```
saxutil  publish \
${SAX_CELL}/${MODEL_NAME} \
${MODEL_CONFIG_PATH} \
${CHECKPOINT_PATH} \
${REPLICA} \
BATCH_SIZE=[1,2,4]
```

```
saxutil  publish \
${SAX_CELL}/${MODEL_NAME} \
${MODEL_CONFIG_PATH} \
${CHECKPOINT_PATH} \
${REPLICA} \
BATCH_SIZE=[8]
```



This may take a while. Monitor the model server pod till the model loading is completed. 

```
kubectl logs <SAX MODEL SERVER POD> -n <YOUR NAMESPACE>
```

Wait till you see a similar message:

```
I1102 14:15:00.962680 134004674082368 servable_model.py:697] loading completed.
```

#### Run smoke test

```

saxutil  lm.generate  ${SAX_CELL}/${MODEL_NAME} "Q: Who is Harry Potter's mother? A:" 
```

If successful the above command should return a list of tokens representing prompt completion. You should see the output similar to:

```
+--------------------------------+-----------+
|            GENERATE            |   SCORE   |
+--------------------------------+-----------+
| Lily Evans. Q: Who is Harry    | -11.23052 |
| Potter's father? A: James      |           |
| Potter. Q: Who are Harry       |           |
| Potter's                       |           |
+--------------------------------+-----------+
```

#### Unpublish the model


To unpublish the model

```
saxutil \
--sax_root=$SAX_ROOT \
unpublish \
${SAX_CELL}/${MODEL_NAME} 
```