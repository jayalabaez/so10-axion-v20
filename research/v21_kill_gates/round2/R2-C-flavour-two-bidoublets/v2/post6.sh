#!/bin/bash
# queue H: after queue E: full main campaign at the best v_R found by the fine scan (2e12, R813)
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
until grep -q "QUEUE E DONE" queue_E.log 2>/dev/null; do sleep 30; done
echo "$(date +%H:%M:%S) start main 2e12" >> queue_H.log
$PY -B run_vr.py main 2e12 R813 I --n 50 --nbh 50 --nx 2 --seeds 10 --hops 10 > /dev/null 2>> queue_H.err
$PY -B floor0.py main_2e+12_R813_I.json >> queue_H.out 2>> queue_H.err
echo "$(date +%H:%M:%S) QUEUE H DONE" >> queue_H.log
