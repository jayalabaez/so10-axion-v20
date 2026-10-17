#!/bin/bash
# R2-A orientation scan of the flavour-capable light contents with the interlacing LP (r2_lp5.py), local constraints
# (heavy gap, light windows, boxes, singlet-channel unitarity |a0| <= 1/2).  usage: lp_scan.sh <listfile: tag content>
D="C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21R2/R2-A-vacuum-two-bidoublets"
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "$D" || exit 1
declare -A SPEC
SPEC[C2]="(1,2)_|Y|=1/2:sub4"
SPEC[C1]="(1,2)_|Y|=1/2:sub4;(8,3)_|Y|=0:sandwich"
SPEC[C1p]="(1,2)_|Y|=1/2:sub4;(1,3)_|Y|=0:sandwich"
SPEC[B1]="(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich"
SPEC[V0]=""
SPEC[D1]="(1,2)_|Y|=1/2:sub1"
SPEC[D2]="(1,2)_|Y|=1/2:sub2"
while read -r tag content extra; do
  content="${content%$''}"; extra="${extra%$''}"; [ -z "$tag" ] && continue
  out="S5_${tag}_${content}"
  if [ -f "${out}.json" ]; then echo "skip $out"; continue; fi
  echo "##### $out  $(date +%T)"
  "$PY" -B r2_lp5.py "$tag" "$out" --light "${SPEC[$content]}" --unitarity 0.5 --no_competitor --no_bfb --no_lightb --outer 6 --iters 400 $extra 2>&1 | grep -E "^outer|^saved|INFEASIBLE|no solution|Error|Traceback" | tail -4
done < "$1"
echo "LPSCAN_DONE $(date +%T)"
