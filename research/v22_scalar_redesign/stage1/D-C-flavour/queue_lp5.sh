#!/bin/bash
# D3 decomposition at SMd (Am45, omega 0, r 0.5, x 4), no SM-singlet competitor cuts unless stated
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
S1="(1,1)_|Y|=0:sub1"
O="--vev_light none --unitarity 0.5 --outer 4 --no_competitor"
$PY -B lp_sm.py SMd L_SMd_D1_deep --light "$S1;(1,2)_|Y|=1/2:sub1" $O --extra_comp deep_endpoints.npz > L_SMd_D1_deep.out 2>&1
$PY -B lp_sm.py SMd L_SMd_D1octa --light "$S1;(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1" $O > L_SMd_D1octa.out 2>&1
$PY -B lp_sm.py SMd L_SMd_D1octb --light "$S1;(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich" $O > L_SMd_D1octb.out 2>&1
$PY -B lp_sm.py SMd L_SMd_EW09 --light "$S1" --ew_target ew_SMd_FU09.npz $O > L_SMd_EW09.out 2>&1
$PY -B lp_sm.py SMd L_SMd_EW05 --light "$S1" --ew_target ew_SMd_FU05.npz $O > L_SMd_EW05.out 2>&1
