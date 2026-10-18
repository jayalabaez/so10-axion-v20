#!/bin/bash
# D3 LPs at one-step points; (1,1)_|Y|=0:sub1 = the S radial mode (m^2 ~ s^2 ~ 1e-6, automatically light; the earlier
# runs without it were degenerate: t forced to ~1e-5).  One LP at a time.
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
S1="(1,1)_|Y|=0:sub1"
for P in SMb SMc SMa; do
  $PY -B lp_sm.py $P L_${P}_V0 --light "$S1" --vev_light none --unitarity 0.5 --outer 3 > L_${P}_V0.out 2>&1
  $PY -B lp_sm.py $P L_${P}_D1 --light "$S1;(1,2)_|Y|=1/2:sub1" --vev_light none --unitarity 0.5 --outer 4 > L_${P}_D1.out 2>&1
done
for P in SMb SMc; do
  $PY -B lp_sm.py $P L_${P}_D1oct --light "$S1;(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1" --vev_light none --unitarity 0.5 --outer 4 --extra_comp deep_endpoints.npz > L_${P}_D1oct.out 2>&1
done
