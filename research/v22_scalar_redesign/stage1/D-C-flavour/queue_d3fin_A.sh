#!/bin/bash
# R5 at the SMf flavour point (cubic rows + stage A/B), then 3 fresh descents
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export DCF_SCRATCH='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3' PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd d3
$PY -B r2a_cubic_for_a.py SMf ew_SMf_FU09.npz > cubic_SMf_EW09.log 2>&1
S1="(1,1)_|Y|=0:sub1"
$PY -B lp_sm.py SMf L_SMf_EW09_A --light "$S1" --ew_target ew_SMf_FU09.npz --vev_light none --unitarity 0.5 --outer 2 --extra_comp deep_endpoints.npz --cubic cubic_ew_SMf_FU09.npz > L_SMf_EW09_A.out 2>&1
$PY -B lp_sm.py SMf L_SMf_EW09_B --light "$S1" --ew_target ew_SMf_FU09.npz --vev_light none --unitarity 0.5 --extra_comp deep_endpoints.npz --cubic cubic_ew_SMf_FU09.npz --stage B --fixU L_SMf_EW09_A.npz --objective max_leff --tmin 0.0005 --leff_light > L_SMf_EW09_B.out 2>&1
for st in random:41:1.0 hsray:2:1.0 random:47:1.5; do
  $PY -B r2_descend.py SMf L_SMf_EW09.npz $st A_$(echo $st | tr ':.' '__') 8 0.01 > desc_A_$(echo $st | tr ':.' '__').out 2>&1
done
