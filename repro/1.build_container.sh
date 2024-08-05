#!/bin/bash

source vars.sh

# Check if container is already running
if [ "$(docker ps -q -f name=${CONTAINER})" ]; then
    echo "--- Container ${CONTAINER} is already running"
else
    echo "--- Building image ${IMAGE}"
    docker build -t ${IMAGE} --build-arg "USER_UID=$(id -u)" --build-arg "USER_GID=$(id -g)" ../.devcontainer/
    echo "--- Running container ${CONTAINER} from image ${IMAGE}"
    docker run -it --gpus all --rm -d \
        --shm-size 1g \
        --ipc host \
        --ulimit memlock=-1 \
        --ulimit stack=67108864 \
        -u vscode \
        -v $(pwd)/../:/${WORKING_DIR}:rw \
        -w ${WORKING_DIR} \
        --name ${CONTAINER} \
        ${IMAGE} || die "Failed to run container ${CONTAINER} from image ${IMAGE}"
    echo "--- Container ${CONTAINER} is running"
fi

echo "--- Updating pip and setuptools..."
docker exec -it ${CONTAINER} bash -c "cd ${WORKING_DIR}; pip install --upgrade pip setuptools"

echo "--- Running post-start..."
docker exec -it ${CONTAINER} bash -c "cd ${WORKING_DIR}; ${WORKING_DIR}/.devcontainer/post_start.sh"

echo "--- Print environment variables..."
docker exec -it ${CONTAINER} bash -c "env"

echo "--- Print pip packages..."
docker exec -it ${CONTAINER} bash -c "pip list --format=columns"