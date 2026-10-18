#!/bin/bash
# Skeptic phase-1 emptiness LPs with the COMPLETE Lb competitor set found through round 3 (deep bank + pool3 + G1/G2
# lower points + G3 lower points), at orientation O11, warm start from the round-3 point.  The tester's vlp.py is run
# READ-ONLY from its folder; all inputs were COPIED into the skeptic big dir and every output goes there
# (V22_VACUUM_BIG points vc.BIG at it).  Variant N: necessary conditions only (sampled BFB rays), as the tester's E run.
# Variant D: with the sufficient dominance certificate eps 1e-3 (the formal-round constraint set).
BS=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum_skeptic/lpdir
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research' OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export V22_VACUUM_BIG='C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_stage2a_big\vacuum_skeptic\lpdir'
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
cd $V
VAR=$1
COMMON="--content Lb --octet --objective phase1 --mu 0 --tmin 1e-3 --banks deep,pool3.npz,G12_lower.npz,G3d_Lb_O11_bank.npz --warm R3d_Lb_O11.npz --uiter 12 --max_reps 150 --leff_min 0.0 --leff_all --final_rounds 1 --final_screen_n 5000 --final_screen_polish 5"
if [ "$VAR" = "N" ]; then
  timeout 6000 $PY -B $V/vlp.py O11 SKP1N_Lb $COMMON > $BS/SKP1N_Lb.out 2>&1
else
  timeout 6000 $PY -B $V/vlp.py O11 SKP1D_Lb $COMMON --bfb_dom 1e-3 > $BS/SKP1D_Lb.out 2>&1
fi
