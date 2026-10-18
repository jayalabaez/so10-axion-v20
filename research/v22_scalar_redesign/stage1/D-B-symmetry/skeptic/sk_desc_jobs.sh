#!/bin/bash
# SKEPTIC: fresh full-486-chart descents (r2_descend.py, R2-A original, copied unedited) from the skeptic's box-8 round-3
# slice point SK_R3_box8_o0 (private DB_LPDIR copy).  Lines of the job file: "start outtag max_rows stop_below".
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_DB_skeptic/lp"
S="C:/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage1/D-B-symmetry/skeptic"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
export DB_LPDIR="$D"
cd "$D" || exit 1
while read -r start otag maxr stopb; do
  stopb="${stopb%$'\r'}"; [ -z "$start" ] && continue
  echo "##### $otag $start $(date +%T)"
  "$PY" -B "$S/r2_descend.py" Am45 SK_R3_box8_o0.npz "$start" "$otag" "$maxr" $stopb 2>&1 | grep -E "^rows|deeper|lower_than_star|Traceback|Error" | tail -20
done < "$1"
echo "DESC_DONE $(date +%T)"
