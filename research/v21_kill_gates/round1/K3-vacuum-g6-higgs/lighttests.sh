#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
T=$1
run() { name=$2; shift 2; ./run.sh k3_lp3.py $T custom --quiet --iters 300 --outer 4 --out ${T}_lt_$name "$@" 2>&1 | grep "^saved\|INFEASIBLE\|no solution"; }
run $T bidoublet --light "(1,2)_|Y|=1/2:sub2"
run $T oct822 --light "(8,2)_|Y|=1/2:sandwich"
run $T oct831 --light "(8,3)_|Y|=0:sandwich"
run $T trip131 --light "(1,3)_|Y|=0:sandwich"
run $T T2_no_bid --light "(8,2)_|Y|=1/2:sandwich;(8,3)_|Y|=0:sandwich;(1,3)_|Y|=0:sandwich"
run $T T2_no_822 --light "(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich;(1,3)_|Y|=0:sandwich"
run $T T2_no_831 --light "(1,2)_|Y|=1/2:sub2;(8,2)_|Y|=1/2:sandwich;(1,3)_|Y|=0:sandwich"
run $T T2_no_131 --light "(1,2)_|Y|=1/2:sub2;(8,2)_|Y|=1/2:sandwich;(8,3)_|Y|=0:sandwich"
run $T bid_822 --light "(1,2)_|Y|=1/2:sub2;(8,2)_|Y|=1/2:sandwich"
run $T bid_831 --light "(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich"
run $T bid_131 --light "(1,2)_|Y|=1/2:sub2;(1,3)_|Y|=0:sandwich"
run $T o831_131 --light "(8,3)_|Y|=0:sandwich;(1,3)_|Y|=0:sandwich"
run $T o822_831 --light "(8,2)_|Y|=1/2:sandwich;(8,3)_|Y|=0:sandwich"
run $T o822_131 --light "(8,2)_|Y|=1/2:sandwich;(1,3)_|Y|=0:sandwich"
echo LIGHTTESTS_DONE
