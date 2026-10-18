#!/bin/bash
# 3 fresh full-486-chart descents from the SMf flavour point (R2-A method)
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
for st in hsray:1:1.0 random:43:1.0 hsray:3:0.7; do
  $PY -B r2_descend.py SMf L_SMf_EW09.npz $st B_$(echo $st | tr ':.' '__') 8 0.01 > desc_B_$(echo $st | tr ':.' '__').out 2>&1
done
