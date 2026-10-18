#!/bin/bash
# D3 at x = 4 (R2-A round-1 Phi17 convention): SMd = (Am45, omega=0, r=0.5), SMe = (p=-a=0.6928, omega=0.2, r=0.7)
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
for spec in "SMd 0.70710678 -0.70710678 0.0 0.5 0.0016 4.0" "SMe 0.69282032 -0.69282032 0.2 0.7 0.0016 4.0"; do
  set -- $spec
  [ -f "$DCF_SCRATCH/$1_blocks.npz" ] || { $PY -B k3_point_rows.py $spec > $1_rows.log 2>&1; $PY -B k3_blocks.py $1 > $1_blocks.log 2>&1; }
done
S1="(1,1)_|Y|=0:sub1"
for P in SMd SMe; do
  $PY -B lp_sm.py $P L_${P}_V0 --light "$S1" --vev_light none --unitarity 0.5 --outer 3 > L_${P}_V0.out 2>&1
  $PY -B lp_sm.py $P L_${P}_D1 --light "$S1;(1,2)_|Y|=1/2:sub1" --vev_light none --unitarity 0.5 --outer 4 > L_${P}_D1.out 2>&1
  $PY -B lp_sm.py $P L_${P}_D1oct --light "$S1;(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1" --vev_light none --unitarity 0.5 --outer 4 --extra_comp deep_endpoints.npz > L_${P}_D1oct.out 2>&1
done
