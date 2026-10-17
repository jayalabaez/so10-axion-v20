#!/bin/sh
cd "C:/Users/jayal/AppData/Local/Temp/claude/c--Users-jayal-Downloads-So10Theory2-So10Theory/d4b271a0-faef-4f94-bc1d-6399a3649e86/scratchpad/wfV21/K3-vacuum-g6-higgs"
./run.sh k3_point_rows.py A20 0.93969262 0.34202014 0.0 1.2e-3 1.6e-3 4.0 && ./run.sh k3_blocks.py A20 > A20_blocks.log 2>&1
./run.sh k3_point_rows.py A70 0.34202014 0.93969262 0.0 1.2e-3 1.6e-3 4.0 && ./run.sh k3_blocks.py A70 > A70_blocks.log 2>&1
./run.sh k3_point_rows.py Am45 0.70710678 -0.70710678 0.0 1.2e-3 1.6e-3 4.0 && ./run.sh k3_blocks.py Am45 > Am45_blocks.log 2>&1
./run.sh k3_point_rows.py W45 0.61237244 0.61237244 0.5 1.2e-3 1.6e-3 4.0 && ./run.sh k3_blocks.py W45 > W45_blocks.log 2>&1
echo ORIENT_DONE
