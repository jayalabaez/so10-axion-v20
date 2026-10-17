#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
until grep -q "CHAIN2_DONE" chain2.log 2>/dev/null; do sleep 30; done
./run.sh k3_higgs.py Am45 Am45_bid_th60.npz 0.1 > higgs_bid_th60.log 2>&1
./run.sh k3_cw.py Am45 Am45_bid_th60.npz 0.58 0.05 5 > cw_bid_th60.log 2>&1
echo CHAIN3_DONE
