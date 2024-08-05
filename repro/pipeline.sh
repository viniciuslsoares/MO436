#!/bin/bash

source vars.sh

echo "--- Building image ${IMAGE}"
./1.build_container.sh 2>&1 | tee 1.build_container.sh.log || { echo "Build failed"; exit 1; }

echo "--- Setting up data..."
./2.setup_data.sh 2>&1 | tee 2.setup_data.sh.log

echo "--- Running experiments..."
./3.run.sh 2>&1 | tee 3.run.sh.log

echo "--- Post processing..."
./4.post_processing.sh 2>&1 | tee 4.post_processing.sh.log

echo "--- Cleaning up..."
./5.cleanup.sh 2>&1 | tee 5.cleanup.sh.log

echo "--- Done"
exit 0