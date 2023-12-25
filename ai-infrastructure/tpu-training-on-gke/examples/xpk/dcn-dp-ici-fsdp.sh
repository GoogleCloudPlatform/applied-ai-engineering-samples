#!/bin/bash
set -e

python3 pedagogical_examples/shardings.py --dcn_data_parallelism=2 --ici_fsdp_parallelism=8 --batch_size=131072 --embedding_dimension=2048

