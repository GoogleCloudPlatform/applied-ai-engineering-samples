```
METADATA=GKE_METADATA
CLUSTER=jk-tpu-training-cluster

gcloud container node-pools update tpu-node-pool-0 \
    --cluster=$CLUSTER \
    --workload-metadata=$METADATA

gcloud container node-pools update tpu-node-pool-1 \
    --cluster=$CLUSTER \
    --workload-metadata=$METADATA
```



gcloud container clusters create jk-gke-test1 \
--region us-central2 \
--scopes=storage-full,gke-default


## GCE sandbox

```
PROJECT=jk-mlops-dev
ZONE=us-central2-b

gcloud config set project $PROJECT
gcloud config set compute/zone $ZONE
```

## Provision a single slice

```
TPU_PREFIX=jk-v4-8
QR_ID=$TPU_PREFIX
ACCELERATOR_TYPE=v4-8
RUNTIME=tpu-ubuntu2204-base

gcloud alpha compute tpus queued-resources create $QR_ID \
--node-id=$TPU_PREFIX \
--accelerator-type=$ACCELERATOR_TYPE \
--runtime-version=$RUNTIME 

```

## Provision multiple slices

```
TPU_PREFIX=jk-v4-16
QR_ID=$TPU_PREFIX
ACCELERATOR_TYPE=v4-16
NODE_COUNT=2
RUNTIME=tpu-ubuntu2204-base

gcloud alpha compute tpus queued-resources create $QR_ID \
--node-prefix=$TPU_PREFIX \
--node-count=$NODE_COUNT \
--accelerator-type=$ACCELERATOR_TYPE \
--runtime-version=$RUNTIME 

```

## Install dependencies

```
python3 multihost_runner.py  --TPU_PREFIX=$TPU_PREFIX --COMMAND="bash setup.sh"
```

## Run training

```
python3 multihost_runner.py  --TPU_PREFIX=$TPU_PREFIX --COMMAND="bash 1xv4-32-1B.sh"
```

