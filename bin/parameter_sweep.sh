#!/bin/bash

# This script is intended to be a helper to run a parameter sweep for the ARSI
# algorithm. Will take several days to run.
#
# Author: Jordan R. Abrahams
# Date: 2018-07-14
# Updated Last: 2018-11-17

for ar in 0.0 0.0625 0.125 0.25 0.5 1.0;
do
  for sc in 0.0 0.0625 0.125 0.25 0.5 1.0;
  do
    ar_name=$(echo ${ar} | tr '.' '_' )
    sc_name=$(echo ${sc} | tr '.' '_' )
    nice -15 pstn-simulate -s 20 -e arsi -t 60 \
        --ar-threshold "$ar" \
        --si-threshold "$sc" \
        -o "$HOME/data/20181117/20181117_mit_dream_${ar_name}__${sc_name}.csv" \
        --mit-parse --stop-point 19 \
        "$HOME/mit_dataset/rover_coordination.json"
  done
done
