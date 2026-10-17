#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
while [ ! -f queue_refit.done ]; do sleep 30; done
$PY -B -W ignore refit.py litNF32 1e13 lit=1,nu=nufit32,hops=4,src=their_extra.json+polish_K2.json > refit_litNF32.log 2>&1
$PY -B -W ignore refit.py litNF6 1e13,3e12 lit=1,hops=5,src=their_extra.json+polish_K2.json > refit_litNF6.log 2>&1
echo QUEUE2_DONE > queue2.done
