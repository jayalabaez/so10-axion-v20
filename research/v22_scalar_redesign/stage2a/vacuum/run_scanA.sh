#!/bin/bash
# Stage A orientation scan: content $1, orientation list $2 (space separated); local + SM-singlet screen + dominance BFB
# + lambda_eff_heavy >= 0 + light trilinears <= 1e-4, U-iterated, no in-loop descents.  Output tag A_<content>_<pt>.
B=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
CT=$1; shift
EXTRA=""
if [ "$CT" != "L0" ]; then EXTRA="--octet"; fi
for PT in "$@"; do
  timeout 3000 $B/run.sh $V/vlp.py $PT A_${CT}_${PT} --content $CT $EXTRA --bfb_dom 1e-3 --uiter 5 --screen --leff_min 0.0 --lightb 1e-4 --max_reps 60 --final_rounds 3 > $B/A_${CT}_${PT}.out 2>&1
  grep "RESULT\|NO FEASIBLE" $B/A_${CT}_${PT}.log | tail -1 | sed "s/^/$CT $PT: /"
done
