#!/bin/bash

source vars.sh

run_python_files_in_order() {
    local py_files=("$@")
    
    for f in "${py_files[@]}"; do
        echo "---- Running ${f}"
        docker exec -it ${CONTAINER} bash -c "export CUDA_VISIBLE_DEVICES=${DEVICES}; mkdir -p ${REPRODUCTION_DIR}/${TASK}; cd ${BEST_RESULT_DIR}; python ${f} 2>&1 | tee ${REPRODUCTION_DIR}/${TASK}/${f}.log"
    done
}

######################

##################### HAR #####################
# export TASK="har"

# export BEST_RESULT_DIR="${WORKING_DIR}/best_results/har"
# run_python_files_in_order "BT_Conv_pretrain.py" "BT_Conv_train.py" "BT_Conv_evaluate.py"
# run_python_files_in_order "BT_GRU_pretrain.py" "BT_GRU_train.py" "BT_GRU_evaluate.py"
# run_python_files_in_order "CPC_Conv_pretrain.py" "CPC_Conv_train.py" "CPC_Conv_evaluate.py"
# run_python_files_in_order "LFR_Conv_pretrain.py" "LFR_Conv_train.py" "LFR_Conv_evaluate.py"
# run_python_files_in_order "LFR_GRU_pretrain.py" "LFR_GRU_train.py" "LFR_GRU_evaluate.py"
# run_python_files_in_order "TNC_Conv_pretrain.py" "TNC_Conv_train.py" "TNC_Conv_evaluate.py"
# run_python_files_in_order "TNC_GRU_pretrain.py" "TNC_GRU_train.py" "TNC_GRU_evaluate.py"

##################### Seismic #####################
export TASK="seismic"

export BEST_RESULT_DIR="${WORKING_DIR}/best_results/seismic"
# run_python_files_in_order "BT_pretrain.py" "BT_train.py" "BT_evaluate.py"
run_python_files_in_order "Byol_pretrain.py" "Byol_train.py" "Byol_evaluate.py"
# run_python_files_in_order "LFR_pretrain.py" "LFR_train.py" "LFR_evaluate.py"
# run_python_files_in_order "SimCLR_pretrain.py" "SimCLR_train.py" "SimCLR_evaluate.py"


echo "--- Experiments are done"
exit 0