#!/bin/bash

source vars.sh
set -x

docker stop ${CONTAINER}
docker rm ${CONTAINER}