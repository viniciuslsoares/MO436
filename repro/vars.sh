#!/bin/bash

export GRUPO="grupo6"
export IMAGE="mo436-${GRUPO}-image"
export CONTAINER="mo436-${GRUPO}-container"

export WORKING_DIR="/workspaces/$(basename $(dirname $PWD))"
export REPRODUCTION_BASE_DIR="${WORKING_DIR}/repro/runs"

export EXEC_ID="$(date +%Y-%m-%d-%H-%M-%S)"
export REPRODUCTION_DIR="${REPRODUCTION_BASE_DIR}/${EXEC_ID}"
export DEVICES=1

die() {
    echo "$1"
    exit 1
}

export -f die