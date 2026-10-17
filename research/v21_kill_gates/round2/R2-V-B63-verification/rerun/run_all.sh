#!/bin/sh
S="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-V-B63-verification"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$S"
for f in b63_verify rep_table dual_dp dual_dp_dressed relics ys_rg; do
  t0=$(date +%s)
  "$PY" -B "$f.py" > "rerun/$f.log" 2>&1
  echo "$f exit=$? secs=$(( $(date +%s) - t0 ))" >> rerun/status.txt
done
echo DONE >> rerun/status.txt
