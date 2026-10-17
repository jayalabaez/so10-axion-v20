#!/bin/bash
# R2-A descent worker: lines "tag solution.npz start outtag max_rows [stop_below]"
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
while read -r tag sol start otag maxr stopb; do
  stopb="${stopb%$'\r'}"; [ -z "$tag" ] && continue
  if [ -f "descend_${otag}.json" ]; then echo "skip $otag"; continue; fi
  echo "##### $otag $start $(date +%T)"
  "$PY" -B r2_descend.py "$tag" "$sol" "$start" "$otag" "$maxr" $stopb 2>&1 | grep -E "^rows|accept|reject|deeper|lower_than_star|Traceback|Error" | tail -40
done < "$1"
echo "DESC_DONE $(date +%T)"
