#!/bin/bash
# usage: bash desc_jobs.sh <tag> <solution npz> <jobfile: otag start>
PY="C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research'
cd "$(dirname "$0")" || exit 1
tag=$1; sol=$2
while read -r otag start; do
  [ -z "$otag" ] && continue
  echo "##### $otag $start $(date +%T)"
  timeout 3000 "$PY" -B dac_descend.py "$tag" "$sol" "$start" "$otag" ${MAXROWS:-10} 1e-6 2>&1 | tail -2
done < "$3"
echo "DESC_DONE $(date +%T)"
