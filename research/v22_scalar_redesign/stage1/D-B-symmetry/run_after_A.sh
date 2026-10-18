#!/bin/bash
# Round-2 feedback for the V1 slice (runs after descent worker A): LP with all x=4 banks + the round-1 V1 banks,
# for the C2-type content (D2) and the C1622-type content; then the tuning-constrained flavour fits.
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_DB/lp"
MY="C:/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage1/D-B-symmetry"
until grep -q DESC_DONE "$D/descA.out"; do sleep 30; done
cd "$D"
BANKS=$(ls descend_P831*_bank.npz descend_R1_*_bank.npz descend_R2_*_bank.npz descend_R3_*_bank.npz descend_N1_*_bank.npz descend_V1A_*_bank.npz | tr '\n' ',' | sed 's/,$//')
cat > "$MY/vac/jobs_R2.txt" <<EOT
V1s_D2_lb_R2 Am45 D2 --extra_comp $BANKS --Ufile V1s_D2_lb.npz --outer 4 --iters 400
V1s_C1622_lb_R2 Am45 C1622 --extra_comp $BANKS --Ufile V1s_D2_lb.npz --outer 4 --iters 400
EOT
bash "$MY/vac/db_lp_jobs.sh" "$MY/vac/jobs_R2.txt" > "$D/R2lp.out" 2>&1
cd "$MY"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
$PY -B v1_flavour.py 8e10 C2 2.8e11 30 12 --tunemin 0.1 --tag v1_C2_8e10_cap_tune01
$PY -B v1_flavour.py 1e13 R622 3.5e13 30 14 --tunemin 0.1 --tag v1_R622_1e13_cap_tune01
$PY -B v1_flavour.py 8e10 C2 2.8e11 30 13 --tunemin 0.01 --tag v1_C2_8e10_cap_tune001
echo AFTER_A_DONE
