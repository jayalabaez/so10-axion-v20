#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
$PY -B d2_cont.py --label L2_A_k01 --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max 1 --Rfile d2c_L2_A_k01_R.npz --nuse 4 --ninit 8 --hops 8 > c_L2_A_k01.log 2>&1
$PY -B d2_cont.py --label L3p_A --MU 1.54e16 --light L3 --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max 1 --eta1 -1 --eps_fixed 1 --seeds 1,2,3 --nuse 3 --ninit 6 --hops 6 > c_L3p_A.log 2>&1
$PY -B d2_cont.py --label L2_A_free --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max 1e6 --Rfile d2c_L2_A_k01_R.npz --nuse 2 --ninit 6 --hops 4 > c_L2_A_free.log 2>&1
