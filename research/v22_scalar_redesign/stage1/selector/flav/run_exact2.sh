#!/bin/sh
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
cd "$(dirname "$0")"
for c in 0.3 0.1; do
$PY -B d2_cont.py --label L2x45_c$c --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max $c --eta1 -1 --eps_fixed 1 --Rfile d2c_L2_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L2x45_c$c.log 2>&1 &
$PY -B d2_cont.py --label L2x210_c$c --siglo 2e12 --sighi 1e15 --kappa 0.01 --c5max $c --eta1 1 --eps_fixed -1 --Rfile d2c_L2_A_k01_R.npz --nuse 3 --ninit 6 --hops 6 > c_L2x210_c$c.log 2>&1 &
wait
done
echo done > run_exact2.done
