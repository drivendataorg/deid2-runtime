#!/bin/bash
set -e

# load .env vars
if [ -f .env ]; then
    cat .env | while read a; do export $a; done
fi

# test configuration
if [ $(which nvidia-smi) ]
then
    docker rm -f sfp-submission-gpu
    docker build --build-arg CPU_GPU=gpu -t sfp-cervical-biopsy/inference runtime
    docker run \
	   --name sfp-submission-gpu \
	   --gpus all \
           --network none \
           --mount type=bind,source=$(pwd)/inference-data,target=/inference/data,readonly \
           --mount type=bind,source=$(pwd)/submission,target=/inference/submission \
	   --shm-size 8g \
           sfp-cervical-biopsy/inference
else
    docker rm -f sfp-submission-cpu
    docker build --build-arg CPU_GPU=cpu -t sfp-cervical-biopsy/inference runtime
    docker run \
	   --name sfp-submission-cpu \
	   --network none \
           --mount type=bind,source=$(pwd)/inference-data,target=/inference/data,readonly \
           --mount type=bind,source=$(pwd)/submission,target=/inference/submission \
	   --shm-size 8g \
           sfp-cervical-biopsy/inference
fi
