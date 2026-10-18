#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
# wait for the first x120 run to finish
while [ ! -f sk_fit_x120_u33_s11.json ]; do sleep 5; done
$PY -B sk_flavour.py x120_126 16 33 none 11 > sk_fit_x120_126_u33.log 2>&1
$PY -B sk_flavour.py x120 16 33 none 23 > sk_fit_x120_u33_s23.log 2>&1
$PY -B sk_flavour.py x120_126 16 5 none 11 > sk_fit_x120_126_u5.log 2>&1
$PY -B sk_flavour.py x120_126 16 33 5e15 11 > sk_fit_x120_126_u33_R5e15.log 2>&1
echo FLAV_QUEUE_DONE > flav_queue.done
