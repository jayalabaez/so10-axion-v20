#!/bin/bash
# queue E: after queue D: 1e11 exact-stage rerun with the corrected unphysical-point penalty (v2c)
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
until grep -q "QUEUE D DONE" queue_D.log 2>/dev/null; do sleep 30; done
echo "$(date +%H:%M:%S) start 1e11 fix" >> queue_E.log
$PY -B run_vr.py mainfix 1e11 R813 I --noproxy main_1e+11_R813_I_proxy.json --nx 2 --seeds 10 --hops 10 > /dev/null 2>> queue_E.err
$PY -B floor0.py mainfix_1e+11_R813_I.json >> queue_E.out 2>> queue_E.err
echo "$(date +%H:%M:%S) QUEUE E DONE" >> queue_E.log
