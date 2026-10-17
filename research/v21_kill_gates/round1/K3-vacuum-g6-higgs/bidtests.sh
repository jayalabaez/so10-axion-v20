#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
for th in 0 20 60; do
  ./run.sh k3_lp3.py Am45 custom --quiet --iters 500 --outer 8 --delta 1e-6 --theta $th --out Am45_bid_th$th --light "(1,2)_|Y|=1/2:sub2" 2>&1 | grep "^saved\|INFEASIBLE\|no solution\|^  (1,2)"
done
./run.sh k3_lp3.py Am45 custom --quiet --iters 500 --outer 8 --delta 1e-6 --theta 0 --eps_lo 1e-6 --eps_hi 1e-4 --out Am45_bid_wide --light "(1,2)_|Y|=1/2:sub2" 2>&1 | grep "^saved\|INFEASIBLE\|no solution\|^  (1,2)"
./run.sh k3_lp3.py Am45 custom --quiet --iters 500 --outer 4 --delta 1e-6 --theta 0 --out Am45_bid1 --light "(1,2)_|Y|=1/2:sub1" 2>&1 | grep "^saved\|INFEASIBLE\|no solution\|^  (1,2)"
echo BIDTESTS_DONE
