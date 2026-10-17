#!/bin/bash
# R2-A global-constraint LP: competitor cuts (exact SM-singlet subspace polynomial search + banks), BFB rays, extra
# descent banks, light-cubic suppression (cubic rows along the chosen EW direction), singlet unitarity |a0| <= 1/2.
# usage: glob_lp.sh <tag> <content C1|C2|C1p> <out> <cubic npz|none> <Ufile|none> [extra args...]
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
tag=$1; content=$2; out=$3; cub=$4; uf=$5; shift 5
case $content in
  C1) spec="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich";;
  C2) spec="(1,2)_|Y|=1/2:sub4";;
  C1p) spec="(1,2)_|Y|=1/2:sub4;(1,3)_|Y|=0:sandwich";;
  B1) spec="(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich";;
esac
args=()
[ "$cub" != "none" ] && args+=(--cubic "$cub")
[ "$uf" != "none" ] && args+=(--Ufile "$uf")
EXTRA="descend_P831_r1s_bank.npz,descend_P831_r2s_bank.npz,descend_P831b_r1s_bank.npz,descend_P831b_r2s_bank.npz"
"$PY" -B r2_lp5.py "$tag" "$out" --light "$spec" --unitarity 0.5 --outer 6 --iters 400 --extra_comp "$EXTRA" "${args[@]}" "$@" 2>&1 | grep -E "^outer|^saved|stalled|competitor lower|runaway|active|INFEASIBLE|Traceback|Error|^screen|^lambda" | tail -30
