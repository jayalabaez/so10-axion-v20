#!/bin/bash
# SKEPTIC: re-run of the designer's decisive round-3 LP (r2_lp6.py, R2-A original, copied unedited) on a PRIVATE copy of the
# inputs (DB_LPDIR = scratchpad/v22_DB_skeptic/lp), plus a box-8 robustness variant.  usage: sk_lp_jobs.sh <out> <extra opts...>
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_DB_skeptic/lp"
S="C:/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage1/D-B-symmetry/skeptic"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
export DB_LPDIR="$D"
cd "$D" || exit 1
BANKS=$(awk 'NR==1{for(i=1;i<=NF;i++) if($i=="--extra_comp") print $(i+1)}' "$S/../vac/jobs_R3.txt")
out="$1"; shift
"$PY" -B "$S/r2_lp6.py" Am45 "$out" --light "(1,2)_|Y|=1/2:sub2" --unitarity 0.5 --extra_comp "$BANKS" --Ufile V1s_D2_lb_box4_R2.npz --outer 4 --iters 400 "$@" 2>&1 | grep -E "^outer|^saved|^lambda|INFEASIBLE|no solution|Error|Traceback|stalled|LP status [1-9]" | tail -14
echo "DONE $out $(date +%T)"
