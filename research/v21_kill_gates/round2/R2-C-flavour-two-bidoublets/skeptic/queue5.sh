#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
$PY -B -W ignore refit.py xflB3 3e12,2e12 "xfl=m_d:0.20;m_s:0.20,hops=4,nst=7,src=refit_litNF6.json+their_extra.json+polish_K2.json" > refit_xflB3.log 2>&1
$PY -B -W ignore refit.py litNF6b 3e12,2e12 "lit=1,hops=5,nst=7,src=refit_litNF6.json+their_extra.json+polish_K2.json" > refit_litNF6b.log 2>&1
echo QUEUE5_DONE > queue5.done
