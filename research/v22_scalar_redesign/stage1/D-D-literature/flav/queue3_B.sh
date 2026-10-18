#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
$PY -B d2_cont.py --label L1_A_k01 --siglo 1e15 --sighi 1e17 --kappa 0.01 --c5max 1 --Rfile d2c_L1_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L1_A_k01.log 2>&1
$PY -B d2_cont.py --label L1_typeII_A --siglo 1e15 --sighi 1e17 --kappa 0.01 --c5max 1 --typeII 1 --Rfile d2c_L1_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L1_typeII_A.log 2>&1
$PY -B d2_cont.py --label L2_A_k02 --siglo 2e12 --sighi 1e15 --kappa 0.02 --c5max 1 --Rfile d2c_L2_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L2_A_k02.log 2>&1
