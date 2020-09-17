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
    docker build --build-arg CPU_GPU=gpu -t deid2/codeexecution runtime
    docker run \
	   --name deid2-submission-gpu \
	   --gpus all \
           --network none \
           --mount type=bind,source=$(pwd)/data,target=/codeexecution/data,readonly \
           --mount type=bind,source=$(pwd)/submission,target=/codeexecution/submission \
	   --shm-size 8g \
           deid2/codeexecution
else
    docker rm -f deid2-submission-cpu
    docker build --build-arg CPU_GPU=cpu -t deid2/codeexecution runtime
    docker run \
	   --name deid2-submission-cpu \
	   --network none \
           --mount type=bind,source=$(pwd)/data,target=/codeexecution/data,readonly \
           --mount type=bind,source=$(pwd)/submission,target=/codeexecution/submission \
	   --shm-size 8g \
           deid2/codeexecution
fi
