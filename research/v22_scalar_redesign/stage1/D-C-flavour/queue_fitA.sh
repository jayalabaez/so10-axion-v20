#!/bin/bash
# D2 queue A (renormalizable one-step fits, chain a)
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for vr in 1e16 3e15 1e15 3e13; do
  $PY -B d2_eft_fit.py G a $vr ren 0.011 3 11 fits/ren_a_${vr}.json 0.01 1500
done
