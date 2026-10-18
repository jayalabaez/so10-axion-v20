#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
$PY -B d2_batch.py --label F2_L1_renorm_sig1e15 --useA 0 --siglo 1e15 --sighi 1e17 --seeds 1,2,3 > F2.log 2>&1
$PY -B d2_batch.py --label F4_L2_A_window --useA 1 --kappa 0.01 --c5max 1 --siglo 2e12 --sighi 1e15 --seeds 1,2,3 > F4.log 2>&1
$PY -B d2_batch.py --label F6_L1_typeII_A_sig1e15 --useA 1 --typeII 1 --kappa 0.01 --c5max 1 --siglo 1e15 --sighi 1e17 --seeds 1,2,3 > F6.log 2>&1
$PY -B d2_batch.py --label F1_L1_renorm_free --useA 0 --siglo 1e9 --sighi 1e17 --seeds 2,3 > F1.log 2>&1
