#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
cd "$(dirname "$0")"
$PY -B d2_cont.py --label L2x45_c1 --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max 1 --eta1 -1 --eps_fixed 1 --Rfile d2c_L2_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L2x45_c1.log 2>&1 &
$PY -B d2_cont.py --label L2x210_c1 --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max 1 --eta1 1 --eps_fixed -1 --Rfile d2c_L2_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L2x210_c1.log 2>&1 &
wait
echo done > run_exact.done
