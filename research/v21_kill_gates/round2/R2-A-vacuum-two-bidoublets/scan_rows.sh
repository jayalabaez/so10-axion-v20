#!/bin/bash
# R2-A: rows (51 exact-X parameter rows at the point) + SM-isotypic blocks for a list of 210 orientations.
# usage: scan_rows.sh <listfile>   (lines: tag p a omega)
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
while read -r tag p a om; do
  [ -z "$tag" ] && continue
  if [ -f "${tag}_blocks.npz" ] && [ -f "${tag}_rows.npz" ]; then echo "skip $tag"; continue; fi
  echo "##### $tag (p,a,omega) = ($p,$a,$om)  $(date +%T)"
  "$PY" -B k3_point_rows.py "$tag" "$p" "$a" "$om" 1.2e-3 1.6e-3 4.0 2>&1 | tail -2
  "$PY" -B k3_blocks.py "$tag" > "${tag}_blocks.log" 2>&1
  grep -E "symmetry tangent rank|gradient rank|Goldstone real dimension|isotypic" "${tag}_blocks.log"
done < "$1"
echo "SCAN_DONE $(date +%T)"
