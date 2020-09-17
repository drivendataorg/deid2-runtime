#!/bin/bash
set -e

# load .env vars
if [ -f .env ]; then
    cat .env | while read a; do export $a; done
fi

# test configuration
docker rm -f deid2-submission || true
docker build -t deid2/codeexecution runtime
docker run \
       --name deid2-submission \
       --network none \
       --mount type=bind,source=$(pwd)/data,target=/codeexecution/data,readonly \
       --mount type=bind,source=$(pwd)/submission,target=/codeexecution/submission \
       --shm-size 8g \
       deid2/codeexecution
