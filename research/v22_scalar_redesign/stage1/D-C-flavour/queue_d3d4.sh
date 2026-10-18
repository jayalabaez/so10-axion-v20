#!/bin/bash
# D3 (SM-orientation LPs at SMa) then D4 (unification MC) -- one process at a time
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3'
cd d3
$PY -B lp_sm.py SMa L_SMa_V0 --light "" --vev_light none --unitarity 0.5 --outer 3 > L_SMa_V0.out 2>&1
$PY -B lp_sm.py SMa L_SMa_D1 --light "(1,2)_|Y|=1/2:sub1" --vev_light none --unitarity 0.5 --outer 4 > L_SMa_D1.out 2>&1
$PY -B lp_sm.py SMa L_SMa_D1oct --light "(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1" --vev_light none --unitarity 0.5 --outer 4 > L_SMa_D1oct.out 2>&1
$PY -B lp_sm.py SMa L_SMa_D1oct_deep --light "(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1" --vev_light none --unitarity 0.5 --outer 4 --extra_comp deep_endpoints.npz > L_SMa_D1oct_deep.out 2>&1
cd ..
$PY -B d4_unif.py d4_unif.json 200 > d4_unif.log 2>&1
