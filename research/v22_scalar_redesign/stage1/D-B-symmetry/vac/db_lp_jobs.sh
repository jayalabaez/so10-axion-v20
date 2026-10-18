#!/bin/bash
# D-B-symmetry D3 screen: r2_lp6.py (R2-A, copied unedited) job runner; data/outputs in the scratchpad workspace (DB_LPDIR).
# Lines: out tag content [extra args...].  Contents: D2 = one light complex bidoublet (+ Delta_R, default VEV block),
# B1 = D2 + (8,3,1)_0 (C0), V0 = no light doublet, C2 = two light bidoublets.
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_DB/lp"
S="C:/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage1/D-B-symmetry/vac"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
export DB_LPDIR="$D"
cd "$D" || exit 1
declare -A SPEC
SPEC[V0]=""
SPEC[D2]="(1,2)_|Y|=1/2:sub2"
SPEC[B1]="(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich"
SPEC[C2]="(1,2)_|Y|=1/2:sub4"
SPEC[C1622]="(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich;(6,2)_|Y|=5/6:sandwich"
while read -r out tag content extra; do
  extra="${extra%$'\r'}"; [ -z "$out" ] && continue; case "$out" in \#*) continue;; esac
  if [ -f "${out}.json" ]; then echo "skip $out"; continue; fi
  echo "##### $out $tag $content $extra $(date +%T)"
  timeout 5400 "$PY" -B "$S/r2_lp6.py" "$tag" "$out" --light "${SPEC[$content]}" --unitarity 0.5 $extra 2>&1 | grep -E "^outer|^saved|^lambda|INFEASIBLE|no solution|Error|Traceback|stalled|objective|LP status [1-9]" | tail -12
done < "$1"
echo "JOBS_DONE $(date +%T)"
