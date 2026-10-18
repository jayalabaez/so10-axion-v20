#!/bin/bash
# R5 check at the flavour composition (SMd, EW09): exact cubic/quartic rows along the light-Higgs direction, then the
# convex stage-B LP maximising the EXACT tree lambda_eff (R2-A method) at fixed light subspaces.
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
until grep -Eq "^saved|Traceback" L_SMd_EW05.out 2>/dev/null; do sleep 10; done
$PY -B r2a_cubic_for_a.py SMd ew_SMd_FU09.npz > cubic_SMd_EW09.log 2>&1
S1="(1,1)_|Y|=0:sub1"
$PY -B lp_sm.py SMd L_SMd_EW09_A --light "$S1" --ew_target ew_SMd_FU09.npz --vev_light none --unitarity 0.5 --outer 2 --no_competitor --cubic cubic_ew_SMd_FU09.npz > L_SMd_EW09_A.out 2>&1
$PY -B lp_sm.py SMd L_SMd_EW09_B --light "$S1" --ew_target ew_SMd_FU09.npz --vev_light none --unitarity 0.5 --no_competitor --cubic cubic_ew_SMd_FU09.npz --stage B --fixU L_SMd_EW09_A.npz --objective max_leff --tmin 0.003 --leff_light > L_SMd_EW09_B.out 2>&1
