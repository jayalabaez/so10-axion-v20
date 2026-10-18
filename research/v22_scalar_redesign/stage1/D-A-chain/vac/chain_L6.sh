#!/bin/bash
cd "$(dirname "$0")"
until grep -q JOBS_DONE L3.out 2>/dev/null; do sleep 10; done
OUTER=4 bash jobs_sm.sh jobs_L6.txt > L6.out 2>&1
if grep -q "saved L6_S2_U8362e_R" L6_S2_U8362e_R.log; then MAXROWS=8 bash desc_jobs.sh S2 L6_S2_U8362e_R.npz jobs_desc3.txt > desc3.out 2>&1; fi
