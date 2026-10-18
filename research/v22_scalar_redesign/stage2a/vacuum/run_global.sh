#!/bin/bash
# Global search (D3) at a coupling point: two vdesc jobs (job splitting first=0/1, every=2), then a merged summary.
# usage: run_global.sh <pt_tag> <solution npz> <out tag> [starts]
B=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
PT=$1; SOL=$2; OUT=$3
STARTS=${4:-"random:11:24,hsray:12:24,ew:0.02/0.05/0.2/0.5/1.0,pert:13:6:0.1,deepend:A0,deepend:Astar,deepend:Arand"}
$B/run.sh $V/vdesc.py $PT $SOL ${OUT}_j0 "$STARTS" --first 0 --every 2 > $B/${OUT}_j0.out 2>&1 &
P0=$!
$B/run.sh $V/vdesc.py $PT $SOL ${OUT}_j1 "$STARTS" --first 1 --every 2 > $B/${OUT}_j1.out 2>&1 &
P1=$!
wait $P0 $P1
$B/run.sh $V/vmerge.py $OUT ${OUT}_j0 ${OUT}_j1
