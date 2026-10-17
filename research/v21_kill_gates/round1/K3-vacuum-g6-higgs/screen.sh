#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
./run.sh k3_eval_points.py deltar deltar_pts.npz 220 > eval_deltar.log 2>&1
for s in Am45_cb_vev_unit.npz Am45_bid_th0.npz Am45_cb_bid_831.npz Am45_bid_th60.npz; do
  echo "##### smsinglet $s"; ./run.sh k3_subspace_fit.py smsinglet_pts.npz $s smsinglet 2>&1 | grep -v "^  V =" 
  echo "##### deltar $s"; ./run.sh k3_subspace_fit.py deltar_pts.npz $s deltar 2>&1 | grep -v "^  V ="
done
echo SCREEN_DONE
