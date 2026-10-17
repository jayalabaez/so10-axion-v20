#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
S="src=refit_xflA.json+refit_xflB.json+refit_litNF6.json+their_extra.json+polish_K2.json"
$PY -B -W ignore refit.py floor5L 1e13 "floor=0.05,hops=4,nst=6,$S" > refit_floor5L.log 2>&1
$PY -B -W ignore refit.py xfl07 1e13 "xfl=m_d:0.07;m_s:0.07,hops=4,nst=6,$S" > refit_xfl07.log 2>&1
$PY -B -W ignore refit.py xfl05 1e13 "xfl=m_d:0.05;m_s:0.05,hops=4,nst=6,$S" > refit_xfl05.log 2>&1
$PY -B -W ignore refit.py xflA3 3e12,3e13 "xfl=m_d:0.10;m_s:0.10,hops=4,nst=8,$S" > refit_xflA3.log 2>&1
echo QUEUE6_DONE > queue6.done
