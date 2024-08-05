#!/bin/bash

source vars.sh

rm -rf results.txt
grep -Rsni -e "F1" -e "IoU" -e "Acc" runs/*/*evaluate* 2>&1 | tee results.txt
echo "Results saved to results.txt"