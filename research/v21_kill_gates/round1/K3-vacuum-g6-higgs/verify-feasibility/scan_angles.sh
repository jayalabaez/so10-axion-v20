#!/bin/bash
# Orientation-angle scan of the pure-210 pair sum rule ((8,3,1)_0 and (1,3,1)_0 both light) and the 126bar (8,2,2)_0
# sum rule, using copies of the researcher's pipeline (rows -> blocks -> sumrules/pair210) in this folder.
V="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs/verify-feasibility"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$V" || exit 1
for th in "$@"; do
  tag="T$th"; tag="${tag/-/m}"
  read p a < <("$PY" -c "import math; t=math.radians($th); print(math.cos(t), math.sin(t))")
  echo "##### theta = $th deg  (p, a) = ($p, $a)  tag = $tag  $(date +%T)"
  "$PY" -B k3_point_rows.py "$tag" "$p" "$a" 0.0 1.2e-3 1.6e-3 4.0 2>&1 | tail -3
  "$PY" -B k3_blocks.py "$tag" 2>&1 | grep -E "symmetry tangent rank|gradient rank|Goldstone real dimension|saved"
  "$PY" -B k3_sumrules.py "$tag" phi 2>&1 | grep -E "rank|\(8,3\)|\(1,3\)"
  "$PY" -B pair210.py "$tag" 2>&1
  "$PY" -B k3_sumrules.py "$tag" sigma 2>&1 | grep -E "rank|\(8,2\)"
  rm -f "${tag}_rows.npz"
done
echo "SCAN_DONE $(date +%T)"
