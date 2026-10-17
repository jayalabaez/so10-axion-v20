#!/bin/bash
# queue G: after queue F: sensitivity of the low-v_R minima to the Delta_R Majorana-coupling bound
# (f <= 2 sqrt(4 pi) = 7.09, i.e. the other Majorana normalisation, and no f bound at all: only |Y126_act| <= 1.5)
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
until grep -q "QUEUE F DONE" queue_F.log 2>/dev/null; do sleep 30; done
SRC=main_3e+12_R622_I.json,main_1e+13_R622_I.json,main_1e+12_R813_I.json,main_1e+11_R813_I.json
echo "$(date +%H:%M:%S) start fh7" >> queue_G.log
R2C_FHMAX=7.09 $PY -B vscan.py fh7 1e12,2e12,3e12 $SRC >> queue_G.out 2>> queue_G.err
echo "$(date +%H:%M:%S) start fhinf" >> queue_G.log
R2C_FHMAX=inf $PY -B vscan.py fhinf 1e12,2e12 $SRC >> queue_G.out 2>> queue_G.err
echo "$(date +%H:%M:%S) QUEUE G DONE" >> queue_G.log
