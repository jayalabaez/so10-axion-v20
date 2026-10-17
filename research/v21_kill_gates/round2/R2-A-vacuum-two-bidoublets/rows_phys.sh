#!/bin/bash
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
while read -r tag p a om r s x; do
  x="${x%$'\r'}"; [ -z "$tag" ] && continue
  if [ -f "${tag}_blocks.npz" ]; then echo "skip $tag"; continue; fi
  echo "##### $tag ($p,$a,$om) r=$r s=$s x=$x $(date +%T)"
  "$PY" -B k3_point_rows.py "$tag" "$p" "$a" "$om" "$r" "$s" "$x" 2>&1 | tail -2
  "$PY" -B k3_blocks.py "$tag" > "${tag}_blocks.log" 2>&1
  grep -E "symmetry tangent rank|gradient rank|Goldstone real dimension" "${tag}_blocks.log"
done < "$1"
echo "ROWS_DONE $(date +%T)"
