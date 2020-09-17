#!/bin/bash
set -e

# load .env vars
if [ -f .env ]; then
    cat .env | while read a; do export $a; done
fi

# test configuration
if [ $(which nvidia-smi) ]
then
    docker rm -f deid2-submission-gpu
    docker build --build-arg CPU_GPU=gpu -t deid2/inference runtime
    docker run \
	   --name deid2-submission-gpu \
	   --gpus all \
           --network none \
           --mount type=bind,source=$(pwd)/inference-data,target=/inference/data,readonly \
           --mount type=bind,source=$(pwd)/submission,target=/inference/submission \
	   --shm-size 8g \
           deid2/inference
else
    docker rm -f deid2-submission-cpu
    docker build --build-arg CPU_GPU=cpu -t deid2/inference runtime
    docker run \
	   --name deid2-submission-cpu \
	   --network none \
           --mount type=bind,source=$(pwd)/inference-data,target=/inference/data,readonly \
           --mount type=bind,source=$(pwd)/submission,target=/inference/submission \
	   --shm-size 8g \
           deid2/inference
fi
