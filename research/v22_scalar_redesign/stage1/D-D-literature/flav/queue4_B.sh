#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
for c in 0.3 0.1 0.03; do
$PY -B d2_cont.py --label L2_A_c$c --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max $c --Rfile d2c_L2_A_k01_R.npz --nuse 2 --ninit 6 --hops 4 > c_L2_A_c$c.log 2>&1
$PY -B d2_cont.py --label L1b_typeII_A_c$c --siglo 1e15 --sighi 1e17 --kappa 0.01 --c5max $c --typeII 1 --Rfile d2c_L1_A_k01_R.npz --nuse 2 --ninit 6 --hops 4 > c_L1b_typeII_A_c$c.log 2>&1
done
$PY -B d2_cont.py --label L1b_typeII_noA --siglo 1e15 --sighi 1e17 --useA 0 --typeII 1 --Rfile d2c_L1_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L1b_typeII_noA.log 2>&1
$PY -B d2_cont.py --label L2_typeII_noA --siglo 2e12 --sighi 1e15 --useA 0 --typeII 1 --Rfile d2c_L2_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L2_typeII_noA.log 2>&1
