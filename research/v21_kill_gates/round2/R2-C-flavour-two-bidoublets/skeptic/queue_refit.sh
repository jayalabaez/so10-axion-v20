#!/bin/bash
# waits for polish_K2 to finish, then runs the robustness refits sequentially
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
while ! grep -q "vR=5.0e+12 R622 BEST" polish_K2.log 2>/dev/null; do
  if ! ps -W 2>/dev/null | grep -q python; then break; fi
  sleep 20
done
$PY -B -W ignore refit.py floor3 3e12,2e12,1e13 floor=0.03,hops=5 > refit_floor3.log 2>&1
$PY -B -W ignore refit.py floor5 3e12,2e12,1e13 floor=0.05,hops=5 > refit_floor5.log 2>&1
$PY -B -W ignore refit.py th23free 3e12,2e12 th23s=10,hops=5 > refit_th23free.log 2>&1
$PY -B -W ignore refit.py nuis1 3e12,2e12 nuis=3,nsig=0.01,hops=5 > refit_nuis1.log 2>&1
$PY -B -W ignore refit.py K1 3e12,2e12 K=1,hops=4 > refit_K1.log 2>&1
$PY -B -W ignore refit.py xT8 3e12 xT=8,hops=4 > refit_xT8.log 2>&1
$PY -B -W ignore refit.py loop1 3e12 loop=1,hops=4 > refit_loop1.log 2>&1
$PY -B -W ignore refit.py ffac2 2e12,1e12 ffac=2,hops=5 > refit_ffac2.log 2>&1
echo QUEUE_DONE > queue_refit.done
