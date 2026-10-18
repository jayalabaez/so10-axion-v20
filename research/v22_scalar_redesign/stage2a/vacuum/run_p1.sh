#!/bin/bash
# phase-1 emptiness LPs (necessary constraints only, strict lifting mu = 0): content $1, pool $2, orientations ...
B=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
CT=$1; POOL=$2; shift; shift
EXTRA=""; if [ "$CT" != "L0" ]; then EXTRA="--octet"; fi
for PT in "$@"; do
  W=""; if [ -f $B/A_${CT}_${PT}.npz ]; then W="--warm A_${CT}_${PT}.npz"; fi
  timeout 5000 $B/run.sh $V/vlp.py $PT E_${CT}_${PT} --content $CT $EXTRA --objective phase1 --mu 0 --tmin 1e-3 --banks deep,$POOL $W --uiter 12 --max_reps 150 --leff_min 0.0 --leff_all --final_rounds 1 --final_screen_n 5000 --final_screen_polish 5 > $B/E_${CT}_${PT}.out 2>&1
  echo "$CT $PT: $(grep 'U-iter' $B/E_${CT}_${PT}.log | tail -1 | cut -c1-120)"
done
