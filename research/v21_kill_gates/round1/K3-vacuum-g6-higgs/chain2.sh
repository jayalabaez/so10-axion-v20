#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
./run.sh k3_higgs.py Am45 Am45_bid_th0.npz 0.1 > higgs_bid_th0.log 2>&1
./run.sh k3_cw.py Am45 Am45_bid_th0.npz 0.58 0.05 6 > cw_bid_th0.log 2>&1
./run.sh k3_eval_points.py smsinglet smsinglet_pts.npz 110 > eval_smsinglet.log 2>&1
echo CHAIN2_DONE
