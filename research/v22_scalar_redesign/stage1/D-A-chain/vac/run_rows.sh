#!/bin/sh
# usage: sh run_rows.sh "<tag> p a omega r s x" ...   (sequential rows + blocks for each point)
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd "$(dirname "$0")"
for spec in "$@"; do
  set -- $spec
  tag=$1
  $PY -B k3_point_rows.py $spec > ${tag}_rows.log 2>&1 && $PY -B k3_blocks.py $tag > ${tag}_blocks.log 2>&1
  echo "done $tag $(date +%T)"
done
