#!/bin/bash
# D3 second valid orientation: SMf = (Am45, omega 0, r 1.0, x 4); V0, D1 and the flavour EW target, with the full
# SM-singlet-subspace competitor/BFB search (the standard R2-A global screen)
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
$PY -B k3_point_rows.py SMf 0.70710678 -0.70710678 0.0 1.0 0.0016 4.0 > SMf_rows.log 2>&1
$PY -B k3_blocks.py SMf > SMf_blocks.log 2>&1
$PY -B make_ew_target.py SMf 0.9 ew_SMf_FU09.npz > ew_SMf.log 2>&1
S1="(1,1)_|Y|=0:sub1"
O="--vev_light none --unitarity 0.5"
$PY -B lp_sm.py SMf L_SMf_V0 --light "$S1" $O --outer 3 > L_SMf_V0.out 2>&1
$PY -B lp_sm.py SMf L_SMf_D1 --light "$S1;(1,2)_|Y|=1/2:sub1" $O --outer 4 --extra_comp deep_endpoints.npz > L_SMf_D1.out 2>&1
$PY -B lp_sm.py SMf L_SMf_EW09 --light "$S1" --ew_target ew_SMf_FU09.npz $O --outer 4 --extra_comp deep_endpoints.npz > L_SMf_EW09.out 2>&1
