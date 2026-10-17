#!/bin/bash
# queue C: starts when queue B is done (keeps <= 2 heavy processes): 2e10 exact-stage rerun, floor-0 continuation,
# content / M_U sensitivity re-polishes.
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
until grep -q "QUEUE B DONE" queue_B.log 2>/dev/null; do sleep 30; done
Q=C
run() { echo "$(date +%H:%M:%S) start $*" >> queue_C.log; $PY -B "$@" >> queue_C.out 2>> queue_C.err; echo "$(date +%H:%M:%S) end $* rc=$?" >> queue_C.log; }
run run_vr.py main 2e10 C2 I --noproxy main_2e+10_C2_I_proxy.json --nx 2 --seeds 10 --hops 10
for f in main_1e+13_R622_I.json main_3e+13_R622_I.json main_1e+14_R622_I.json main_3e+12_R622_I.json main_2e+10_C2_I.json; do
  [ -f "$f" ] && run floor0.py "$f"
done
run sens.py main_1e+13_R622_I.json C1 C1 2.18e15
run sens.py main_1e+13_R622_I.json C2 C2 6.05e15
run sens.py main_3e+13_R622_I.json R813 R813 2.4e16
echo "$(date +%H:%M:%S) QUEUE C DONE" >> queue_C.log
