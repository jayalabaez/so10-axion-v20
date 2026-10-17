#!/bin/bash
# queue F: after queue C: theta23-free fit (sigma(sin^2 th23) = 10, i.e. theta23 dropped) at v_R = 3e12
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
until grep -q "QUEUE C DONE" queue_C.log 2>/dev/null; do sleep 30; done
echo "$(date +%H:%M:%S) start noth23" >> queue_F.log
$PY -B run_vr.py noth23 3e12 R622 I --th23 0.47,10 --n 20 --nbh 20 --nx 1 --seeds 8 --hops 8 > /dev/null 2>> queue_F.err
echo "$(date +%H:%M:%S) QUEUE F DONE" >> queue_F.log
