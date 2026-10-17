#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
until grep -q "COMBOS_DONE" combos.log 2>/dev/null; do sleep 20; done
for f in 0.3 1.0 3.0; do
  ./run.sh k3_lp3.py Am45 custom --quiet --iters 500 --outer 6 --delta 1e-6 --theta 0 --mix_min $f --out Am45_mix$f --light "(1,2)_|Y|=1/2:sub2" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
done
./run.sh k3_lp3.py Am45 custom --quiet --iters 500 --outer 6 --delta 1e-6 --theta 0 --mix_min 1.0 --unitarity 0.5 --box_quartic 20 --box_cubic 20 --box_mass 400 --out Am45_mix1_unit --light "(1,2)_|Y|=1/2:sub2" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
echo COMBOS2_DONE
