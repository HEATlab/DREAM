#!/bin/bash

# This script is intended to be a helper to run a parameter sweep for the ARSI
# algorithm. Will take several days to run.
#
# Author: Jordan R. Abrahams
# Date: 2018-07-14

for ar in 0.0 0.0625 0.125 0.25 0.5 1.0;
do
  for si in 0.0 0.0625 0.125 0.25 0.5 1.0;
  do
    ar_name=$(echo ${ar} | tr '.' '_' )
    si_name=$(echo ${si} | tr '.' '_' )
    nice -10 pstn-simulate -s 100 -e arsi -t 60 \
        --ar-threshold "$ar" \
        --si-threshold "$si" \
        -o "$HOME/data/20180714/20180714_arsi_${ar_name}__${si_name}.csv" \
        "$HOME/sim_files"
  done
done
