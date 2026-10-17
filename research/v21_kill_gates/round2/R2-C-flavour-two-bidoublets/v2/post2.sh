#!/bin/bash
# queue D: after queue A: exact v_R continuation scan (fine grid) from the best main-run points
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
until grep -q "QUEUE A DONE" queue_A.log 2>/dev/null; do sleep 30; done
echo "$(date +%H:%M:%S) start vscan" >> queue_D.log
SRC=main_3e+12_R622_I.json,main_1e+13_R622_I.json
[ -f main_1e+12_R813_I.json ] && SRC=$SRC,main_1e+12_R813_I.json
[ -f main_1e+11_R813_I.json ] && SRC=$SRC,main_1e+11_R813_I.json
$PY -B vscan.py fine 3e11,5e11,1e12,2e12,3e12,5e12,1e13,2e13 $SRC >> queue_D.out 2>> queue_D.err
echo "$(date +%H:%M:%S) QUEUE D DONE rc=$?" >> queue_D.log
