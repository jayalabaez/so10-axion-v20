#!/bin/bash
# R2-A (resumed run) orientation scan for the R2-B rescue contents C1+(8,1,3)_0 and C1+(6,2,2)_{2/3} (and re-runs),
# local constraints only (heavy gap, light windows, boxes, singlet unitarity |a0| <= 1/2).  usage: lp_scan2.sh <listfile>
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
declare -A SPEC
SPEC[C2]="(1,2)_|Y|=1/2:sub4"
SPEC[C1]="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich"
SPEC[C1p]="(1,2)_|Y|=1/2:sub4;(1,3)_|Y|=0:sandwich"
SPEC[C1813]="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=1:sandwich;(8,1)_|Y|=0:sub1"
SPEC[C1622]="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich;(6,2)_|Y|=5/6:sandwich"
SPEC[C2813]="(1,2)_|Y|=1/2:sub4;(8,1)_|Y|=1:sandwich;(8,1)_|Y|=0:sub1"
SPEC[C2622]="(1,2)_|Y|=1/2:sub4;(6,2)_|Y|=1/6:sandwich;(6,2)_|Y|=5/6:sandwich"
while read -r tag content extra; do
  content="${content%$'\r'}"; extra="${extra%$'\r'}"; [ -z "$tag" ] && continue
  out="S5_${tag}_${content}"
  if [ -f "${out}.json" ]; then echo "skip $out"; continue; fi
  echo "##### $out  $(date +%T)"
  timeout 900 "$PY" -B r2_lp5.py "$tag" "$out" --light "${SPEC[$content]}" --unitarity 0.5 --no_competitor --no_bfb --no_lightb --outer 6 --iters 400 $extra 2>&1 | grep -E "^outer|^saved|INFEASIBLE|no solution|Error|Traceback|stalled" | tail -5
done < "$1"
echo "LPSCAN_DONE $(date +%T)"
