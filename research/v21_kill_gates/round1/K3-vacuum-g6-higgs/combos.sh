#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
until grep -q "BIDTESTS_DONE" bidtests.log 2>/dev/null && grep -q "SINGLES_DONE" singles.log 2>/dev/null; do sleep 20; done
run() { name=$1; shift; ./run.sh k3_lp3.py Am45 custom --quiet --iters 500 --outer 6 --delta 1e-6 --theta 0 --out Am45_cb_$name "$@" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"; }
run bid_831 --light "(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich"
run bid_131 --light "(1,2)_|Y|=1/2:sub2;(1,3)_|Y|=0:sandwich"
run bid_822 --light "(1,2)_|Y|=1/2:sub2;(8,2)_|Y|=1/2:sandwich"
run T2 --light "(1,2)_|Y|=1/2:sub2;(8,2)_|Y|=1/2:sandwich;(8,3)_|Y|=0:sandwich;(1,3)_|Y|=0:sandwich"
run o831_131 --light "(8,3)_|Y|=0:sandwich;(1,3)_|Y|=0:sandwich"
run vev_unit --unitarity 0.5 --box_quartic 20 --box_cubic 20 --box_mass 400
run bid_unit --unitarity 0.5 --box_quartic 20 --box_cubic 20 --box_mass 400 --light "(1,2)_|Y|=1/2:sub2"
echo COMBOS_DONE
