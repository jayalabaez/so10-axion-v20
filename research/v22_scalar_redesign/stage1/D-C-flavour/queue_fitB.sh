#!/bin/bash
# D2 queue B (one-step + O5 d=5 operator, chain a, eps = |Phi|/M_Pl,red = 0.011)
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for vr in 1e16 3e15 1e15; do
  $PY -B d2_eft_fit.py G a $vr o5 0.011 3 21 fits/o5_a_${vr}.json 0.01 1500
done
