#!/bin/sh
# usage: ./run.sh script.py args...  (runs with the required env, from the scratch dir)
export MSYS2_ARG_CONV_EXCL="*" MSYS_NO_PATHCONV=1
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SO10_PUBLISHED_API_ROOT='C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo'
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
exec "C:/Users/jayal/AppData/Local/Programs/Python/Python312/python.exe" -B "$@"
