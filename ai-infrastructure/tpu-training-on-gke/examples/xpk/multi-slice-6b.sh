#!/bin/bash
set -e

export LIBTPU_INIT_ARGS="--xla_enable_async_all_gather=true TPU_MEGACORE=MEGACORE_DENSE"

python3 MaxText/train.py MaxText/configs/base.yml \
run_name=$WORKLOAD_ID \
dataset_path=$DATASETS_URI \
base_output_directory=gs://$ARTIFACT_REPOSITORY_BUCKET_NAME/runs \
steps=200 log_period=50 save_period=100 \
per_device_batch_size=16 \
dcn_data_parallelism=2 ici_fsdp_parallelism=16 \
remat_policy=full \
base_emb_dim=4096 base_num_heads=16 base_mlp_dim=16384 head_dim=256 base_num_decoder_layers=32

