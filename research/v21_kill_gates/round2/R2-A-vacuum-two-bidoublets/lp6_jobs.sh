#!/bin/bash
# R2-A (resumed): generic r2_lp6.py job runner.  Lines: out tag content [extra args...]; content in
# C2/C1/C1p/C1622/C1813 (two light bidoublets: sub4) and C2e/C1e/C1622e/C1pe (EW target: sub3), V0/D1/D2 (G3211 tests).
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
declare -A SPEC
SPEC[C2]="(1,2)_|Y|=1/2:sub4"
SPEC[C1]="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich"
SPEC[C1p]="(1,2)_|Y|=1/2:sub4;(1,3)_|Y|=0:sandwich"
SPEC[C1622]="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich;(6,2)_|Y|=5/6:sandwich"
SPEC[C2e]="(1,2)_|Y|=1/2:sub3"
SPEC[C1e]="(1,2)_|Y|=1/2:sub3;(8,3)_|Y|=0:sandwich"
SPEC[C1pe]="(1,2)_|Y|=1/2:sub3;(1,3)_|Y|=0:sandwich"
SPEC[C1622e]="(1,2)_|Y|=1/2:sub3;(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich;(6,2)_|Y|=5/6:sandwich"
SPEC[V0]=""
SPEC[B1]="(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich"
SPEC[D1]="(1,2)_|Y|=1/2:sub1"
SPEC[D2]="(1,2)_|Y|=1/2:sub2"
while read -r out tag content extra; do
  extra="${extra%$'\r'}"; [ -z "$out" ] && continue; case "$out" in \#*) continue;; esac
  if [ -f "${out}.json" ]; then echo "skip $out"; continue; fi
  echo "##### $out $tag $content $extra $(date +%T)"
  timeout 2400 "$PY" -B r2_lp6.py "$tag" "$out" --light "${SPEC[$content]}" --unitarity 0.5 --outer 6 --iters 400 $extra 2>&1 | grep -E "^outer|^saved|INFEASIBLE|no solution|Error|Traceback|stalled|EW |LP status [1-9]" | tail -6
done < "$1"
echo "JOBS_DONE $(date +%T)"
