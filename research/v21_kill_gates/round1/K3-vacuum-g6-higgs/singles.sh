#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
for T in "$@"; do
  ./run.sh k3_lp3.py $T vevonly --quiet --iters 400 --outer 3 --out ${T}_lt_vevonly 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
  ./run.sh k3_lp3.py $T custom --quiet --iters 400 --outer 4 --out ${T}_lt_bidoublet --light "(1,2)_|Y|=1/2:sub2" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
  ./run.sh k3_lp3.py $T custom --quiet --iters 400 --outer 3 --out ${T}_lt_oct822 --light "(8,2)_|Y|=1/2:sandwich" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
  ./run.sh k3_lp3.py $T custom --quiet --iters 400 --outer 3 --out ${T}_lt_oct831 --light "(8,3)_|Y|=0:sandwich" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
  ./run.sh k3_lp3.py $T custom --quiet --iters 400 --outer 3 --out ${T}_lt_trip131 --light "(1,3)_|Y|=0:sandwich" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"
done
echo SINGLES_DONE
