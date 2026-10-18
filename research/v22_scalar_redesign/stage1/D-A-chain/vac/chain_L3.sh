#!/bin/bash
cd "$(dirname "$0")"
until grep -q "chi2_min" ../flavour/run_U8362_d5_f0.01.log 2>/dev/null; do sleep 10; done
OUTER=4 bash jobs_sm.sh jobs_L3.txt > L3.out 2>&1
