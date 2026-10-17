#!/bin/bash
# usage: desc_jobs.sh <solution npz> <tag> <prefix> <start1> [<start2> ...]   (runs sequentially)
S="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets/skeptic"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$S" || exit 1
sol=$1; tag=$2; pre=$3; shift 3; i=0
for st in "$@"; do i=$((i+1)); timeout 2400 "$PY" -B sk_descend.py "$sol" "$tag" "$st" "${pre}_$i" 10 0.01 > /dev/null 2>&1; tail -1 "${pre}_$i.log"; done
echo DESC_DONE
