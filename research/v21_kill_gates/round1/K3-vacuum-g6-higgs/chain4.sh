#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
until grep -q "CHAIN3_DONE" chain3.log 2>/dev/null && grep -q "COMBOS2_DONE" combos2.log 2>/dev/null; do sleep 30; done
if [ -f Am45_mix1_unit.npz ]; then ./run.sh k3_higgs.py Am45 Am45_mix1_unit.npz 0.1 > higgs_mix1_unit.log 2>&1; ./run.sh k3_unitarity.py Am45_mix1_unit.npz > unit_mix1_unit.log 2>&1; fi
if [ -f Am45_cb_bid_unit.npz ]; then ./run.sh k3_higgs.py Am45 Am45_cb_bid_unit.npz 0.1 > higgs_bid_unit.log 2>&1; ./run.sh k3_unitarity.py Am45_cb_bid_unit.npz > unit_bid_unit.log 2>&1; fi
if [ -f Am45_cb_vev_unit.npz ]; then ./run.sh k3_unitarity.py Am45_cb_vev_unit.npz > unit_vev_unit.log 2>&1; fi
echo CHAIN4_DONE
