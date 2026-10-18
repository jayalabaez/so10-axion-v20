#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
$PY -B sk_lambda.py 0.07 > sk_lambda.log 2>&1
$PY -B sk_descend.py hdir:0.05 H05 8 > sk_descend_H05.out 2>&1
$PY -B sk_descend.py cont CONT 7 > sk_descend_CONT.out 2>&1
$PY -B sk_descend.py ray:4242 R4242 7 > sk_descend_R4242.out 2>&1
echo D3_CHAIN_DONE > d3_chain.done
