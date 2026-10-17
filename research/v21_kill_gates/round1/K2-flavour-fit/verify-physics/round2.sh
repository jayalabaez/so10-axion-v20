#!/bin/bash
# second round once hop_T3_0.json exists: (a) theta23 profile from the best points, (b) top-down refit of the hop best
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
nohup $PY -B profile23.py T3 hop_T3_0.json de_T3_0.json > profile23_T3.log 2>&1 &
K2_TD_N=2 K2_TD_NFEV=600 nohup $PY -B td.py T3 hop_T3_0.json hop_T3_0_td.json > td_hop0.log 2>&1 &
echo round2 launched
