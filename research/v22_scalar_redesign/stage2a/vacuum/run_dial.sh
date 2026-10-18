#!/bin/bash
B=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
COMMON="--content Lb --octet --bfb_dom 1e-3 --warm A_Lb_O11.npz --banks deep,pool3.npz --uiter 4 --screen --lightb 1e-4 --max_reps 120 --final_rounds 2"
timeout 3000 $B/run.sh $V/vlp.py O11 L_nolam $COMMON > $B/L_nolam.out 2>&1
echo "nolam: $(grep 'RESULT' $B/L_nolam.log | cut -c1-80) $(grep 'lambda:' $B/L_nolam.log)"
for L in 0.4 0.9; do
  timeout 3000 $B/run.sh $V/vlp.py O11 L_min$L $COMMON --leff_min $L --leff_all > $B/L_min$L.out 2>&1
  echo "lmin $L: $(grep 'RESULT\|NO FEASIBLE' $B/L_min$L.log | cut -c1-80) $(grep 'lambda:' $B/L_min$L.log)"
done
