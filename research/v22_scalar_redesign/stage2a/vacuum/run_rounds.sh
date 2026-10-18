#!/bin/bash
# Formal feedback rounds k = K0..3 for one cell: LP (dominance BFB, all banks + previous global-search lower points)
# -> global search (two vdesc jobs) -> merge.  usage: run_rounds.sh <pt> <content> <tag> <K0> <warm npz> <bank list> <starts>
B=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
PT=$1; CT=$2; TAG=$3; K0=$4; WARM=$5; BANKS=$6; STARTS=$7
cd $B
for K in $(seq $K0 3); do
  timeout 9000 $B/run.sh $V/vlp.py $PT R${K}d_${TAG} --content $CT --octet --bfb_dom 1e-3 --warm $WARM --banks $BANKS --uiter 4 --screen --leff_min 0.0 --leff_all --lightb 1e-4 --max_reps 120 --final_rounds 4 > $B/R${K}d_${TAG}.out 2>&1
  echo "round $K LP: $(grep 'RESULT\|NO FEAS' $B/R${K}d_${TAG}.log | tail -1 | cut -c1-200)"
  grep -q RESULT $B/R${K}d_${TAG}.log || break
  bash $V/run_global.sh $PT R${K}d_${TAG}.npz G${K}d_${TAG} "$STARTS" > $B/G${K}d_${TAG}.txt 2>&1
  echo "round $K global: $(python -c "import json; d=json.load(open('G${K}d_${TAG}.json')); print({k: d[k] for k in ['n_descents','n_lower','n_runaway','deepest_finite']})")"
  WARM=R${K}d_${TAG}.npz
  BANKS=$BANKS,G${K}d_${TAG}_bank.npz
done
