#!/bin/bash
# usage: queue.sh A|B   (two sequential job queues; at most 2 heavy processes in total)
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
PY=/c/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe
MAIN="--n 50 --nbh 50 --nx 2 --seeds 10 --hops 10"
DIAG="--n 20 --nbh 20 --nx 1 --seeds 6 --hops 6"
run() { echo "$(date +%H:%M:%S) start $*" >> queue_$Q.log; $PY -B run_vr.py "$@" > /dev/null 2>> queue_$Q.err; echo "$(date +%H:%M:%S) end $* rc=$?" >> queue_$Q.log; }
Q=$1
if [ "$Q" = "A" ]; then
  run main 1e13 R622 I $MAIN
  run main 3e12 R622 I $MAIN
  run main 1e12 R813 I $MAIN
  run main 1e11 R813 I $MAIN
  run typeII 1e13 R622 II $DIAG
  run nosk 1e13 R622 I --nu nufit60_nosk $DIAG
fi
if [ "$Q" = "B" ]; then
  run main 2e10 C2 I $MAIN
  run main 3e13 R622 I $MAIN
  run main 1e14 R622 I $MAIN
  run litera 1e13 R622 I --nu nufit32 --err lit $DIAG
  run nufit32 1e13 R622 I --nu nufit32 $DIAG
  run prof040 1e13 R622 I --th23 0.40,0.003 $DIAG
  run prof045 1e13 R622 I --th23 0.45,0.003 $DIAG
fi
echo "$(date +%H:%M:%S) QUEUE $Q DONE" >> queue_$Q.log
