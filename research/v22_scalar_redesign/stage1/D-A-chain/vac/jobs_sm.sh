#!/bin/bash
# D-A-chain: dac_lpsm.py job runner (copy of R2-A lp6_jobs.sh logic). Lines: out tag content [extra args...]
# SM-direct vacuum: --vev_light sm (only the S radial mode light); contents:
#   V0 bare SM-direct vacuum; D1 one light SM doublet; U8362 = D1 + (8,3)_0 + (6,2)_{1/6}; U6381 = D1 + (6,3)_{1/3} + (8,1)_0;
#   U8381 = D1 + (8,3)_0 + (8,1)_0
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
cd "$(dirname "$0")" || exit 1
declare -A SPEC
SPEC[V0]=""
SPEC[D1]="(1,2)_|Y|=1/2:sub1"
SPEC[U8362]="(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich"
SPEC[U6381]="(1,2)_|Y|=1/2:sub1;(6,3)_|Y|=1/3:sandwich;(8,1)_|Y|=0:sub1"
SPEC[U8381]="(1,2)_|Y|=1/2:sub1;(8,3)_|Y|=0:sandwich;(8,1)_|Y|=0:sub1"
SPEC[D1e]=""
SPEC[U8362e]="(8,3)_|Y|=0:sandwich;(6,2)_|Y|=1/6:sandwich"
SPEC[U6381e]="(6,3)_|Y|=1/3:sandwich;(8,1)_|Y|=0:sub1"
SPEC[U6362]="(1,2)_|Y|=1/2:sub1;(6,3)_|Y|=1/3:sandwich;(6,2)_|Y|=1/6:sandwich"
while read -r out tag content extra; do
  extra="${extra%$'\r'}"; [ -z "$out" ] && continue; case "$out" in \#*) continue;; esac
  if [ -f "${out}.json" ]; then echo "skip $out"; continue; fi
  echo "##### $out $tag $content $extra $(date +%T)"
  timeout 3000 "$PY" -B dac_lpsm.py "$tag" "$out" --light "${SPEC[$content]}" --vev_light sm --unitarity 0.5 --outer ${OUTER:-6} --iters 400 $extra 2>&1 | grep -E "^outer|^saved|INFEASIBLE|no solution|Error|Traceback|stalled|EW |LP status [1-9]|competitor lower" | tail -8
done < "$1"
echo "JOBS_DONE $(date +%T)"
