#!/bin/bash
# D-B-symmetry descent worker (r2_descend.py from R2-A, copied unedited): lines "tag solution.npz start outtag max_rows [stop_below]"
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_DB/lp"
S="C:/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage1/D-B-symmetry/vac"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
export DB_LPDIR="$D"
cd "$D" || exit 1
while read -r tag sol start otag maxr stopb; do
  stopb="${stopb%$'\r'}"; [ -z "$tag" ] && continue
  if [ -f "descend_${otag}.json" ]; then echo "skip $otag"; continue; fi
  echo "##### $otag $start $(date +%T)"
  "$PY" -B "$S/r2_descend.py" "$tag" "$sol" "$start" "$otag" "$maxr" $stopb 2>&1 | grep -E "^rows|accept|reject|deeper|lower_than_star|Traceback|Error" | tail -40
done < "$1"
echo "DESC_DONE $(date +%T)"
