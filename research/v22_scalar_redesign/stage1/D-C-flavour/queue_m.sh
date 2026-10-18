#!/bin/bash
# targeted test of the 'H-mass' driver: |mass^2| box 40 -> 4 (no large bare-mass cancellations), flavour Higgs at SMf with
# screen + deep(fb1) cuts, |kappaH| <= 0.5; then 3 fresh descents
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
$PY -B lp_sm.py SMf L_SMf_EW09_m4 --light "(1,1)_|Y|=0:sub1" --ew_target ew_SMf_FU09.npz --vev_light none --unitarity 0.5 --outer 4 --extra_comp deep_endpoints_fb1.npz --abs_bound "re::O12:0.5,im::O12:0.5" --box_mass 4 > L_SMf_EW09_m4.out 2>&1
grep -q "^saved" L_SMf_EW09_m4.out || exit 0
$PY -B r2_descend.py SMf L_SMf_EW09_m4.npz hsray:1:1.0 M_hsray1 8 0.01 > desc_M_hsray1.out 2>&1 &
$PY -B r2_descend.py SMf L_SMf_EW09_m4.npz random:41:1.0 M_rnd41 8 0.01 > desc_M_rnd41.out 2>&1
wait
$PY -B r2_descend.py SMf L_SMf_EW09_m4.npz hsray:2:1.0 M_hsray2 8 0.01 > desc_M_hsray2.out 2>&1
