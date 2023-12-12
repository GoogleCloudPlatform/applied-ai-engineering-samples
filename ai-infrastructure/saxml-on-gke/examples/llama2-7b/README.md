# Deploying  Llama-2 7B model

*Work in progress*

## Download the Llama-2 7B checkpoint

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

