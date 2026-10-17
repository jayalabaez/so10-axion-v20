#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
$PY -B -W ignore refit.py xflC 1e13 "xfl=m_u:0.30;m_c:0.13;m_d:0.17;m_s:0.21,hops=4,src=their_extra.json+polish_K2.json" > refit_xflC.log 2>&1
$PY -B -W ignore refit.py xflB 1e13 "xfl=m_d:0.20;m_s:0.20,hops=4,src=their_extra.json+polish_K2.json" > refit_xflB.log 2>&1
$PY -B -W ignore refit.py xflA 1e13 "xfl=m_d:0.10;m_s:0.10,hops=4,src=their_extra.json+polish_K2.json" > refit_xflA.log 2>&1
echo QUEUE4_DONE > queue4.done
