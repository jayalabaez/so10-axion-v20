#!/bin/bash
# D3 decomposition: local realisability of one light doublet (+ colour octets) without the SM-singlet-subspace
# competitor cuts (BFB rays kept), and the same with only the 52 R2-A deep endpoints as competitors.
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
S1="(1,1)_|Y|=0:sub1"
$PY -B lp_sm.py SMd L_SMd_D1_nocomp --light "$S1;(1,2)_|Y|=1/2:sub1" --vev_light none --unitarity 0.5 --outer 4 --no_competitor > L_SMd_D1_nocomp.out 2>&1
$PY -B lp_sm.py SMd L_SMd_D1oct_nocomp_deep --light "$S1;(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1" --vev_light none --unitarity 0.5 --outer 4 --no_competitor --extra_comp deep_endpoints.npz > L_SMd_D1oct_nocomp_deep.out 2>&1
