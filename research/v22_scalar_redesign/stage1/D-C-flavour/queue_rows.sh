#!/bin/bash
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2
cd d3
for spec in "SMb 0.70710678 -0.70710678 0.0 0.5 0.0016 1.4" "SMc 0.69282032 -0.69282032 0.2 0.7 0.0016 1.4"; do
  set -- $spec
  $PY -B k3_point_rows.py $spec > $1_rows.log 2>&1
  $PY -B k3_blocks.py $1 > $1_blocks.log 2>&1
done
