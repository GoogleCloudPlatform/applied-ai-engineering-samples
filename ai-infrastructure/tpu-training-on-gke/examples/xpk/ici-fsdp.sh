#!/bin/bash
set -e

python3 pedagogical_examples/shardings.py --ici_fsdp_parallelism=16 --batch_size=131072 --embedding_dimension=2048

