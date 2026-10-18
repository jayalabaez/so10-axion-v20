#!/bin/bash
B=/c/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/v22_stage2a_big/vacuum
V=/c/Users/jayal/Downloads/So10Theory2/So10Theory/_v22research/research/v22_scalar_redesign/stage2a/vacuum
for PT in O1 O2 O3 O9 O10 O11 test1; do
  for DOM in 0 1e-3; do
    timeout 900 $B/run.sh $V/vlp.py $PT QLa_${PT}_$DOM --content La --octet --bfb_dom $DOM --banks "" --no_rays --no_subbfb --uiter 5 --max_reps 2 --final_rounds 1 --final_screen_n 2000 --final_screen_polish 3 > /dev/null 2>&1
    echo "La $PT dom=$DOM: $(grep 'RESULT\|NO FEAS' $B/QLa_${PT}_$DOM.log | tail -1 | cut -c1-110)"
  done
done
