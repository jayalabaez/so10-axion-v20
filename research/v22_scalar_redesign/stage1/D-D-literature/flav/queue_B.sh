#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
$PY -B d2_batch.py --label F3_L1_A_sig1e15 --useA 1 --kappa 0.01 --c5max 1 --siglo 1e15 --sighi 1e17 --seeds 1,2,3 > F3.log 2>&1
$PY -B d2_batch.py --label F5_L2_A_k02 --useA 1 --kappa 0.02 --c5max 1 --siglo 2e12 --sighi 1e15 --seeds 1,2,3 > F5.log 2>&1
$PY -B d2_batch.py --label F7_L2_A_free --useA 1 --kappa 0.01 --c5max 1e6 --siglo 2e12 --sighi 1e15 --seeds 1,2 > F7.log 2>&1
