#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
while ! grep -q "BEST exact\|Traceback" proxy_p3e12.log; do sleep 30; done
$PY -B -W ignore skproxy.py p2e12 2e12 12 5 > proxy_p2e12.log 2>&1
$PY -B -W ignore skproxy.py p1e13 1e13 12 4 > proxy_p1e13.log 2>&1
echo QUEUE3_DONE > queue3.done
