#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
timeout 1500 $PY -B dac_flavrun.py N8362 0.01 d5 14 0.5 > run_N8362_d5_f0.01.log 2>&1
timeout 1500 $PY -B dac_flavrun.py N8362 0.01 d5 14 0.5 5e15 > run_N8362_d5_f0.01_R5e15.log 2>&1
