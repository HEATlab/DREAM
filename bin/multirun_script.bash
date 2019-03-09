#!/bin/bash
#nice -10 pstn-simulate -s 100 -e early -t 60 -o ~/data/20180719/20180719_early.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e srea -t 60 -o ~/data/20180719/20180719_srea.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea -t 60 -o ~/data/20180719/20180719_drea.csv ~/sim_files

#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.0 -o ~/data/20180719/20180719_drea_si_0_0.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.1 -o ~/data/20180719/20180719_drea_si_0_1.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.0 -o ~/data/20180719/20180719_drea_si_0_0625.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.0625 -o ~/data/20180719/20180719_drea_si_0_0625.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.125 -o ~/data/20180719/20180719_drea_si_0_125.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.25 -o ~/data/20180719/20180719_drea_si_0_25.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.375 -o ~/data/20180719/20180719_drea_si_0_375.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.5 -o ~/data/20180719/20180719_drea_si_0_5.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.75 -o ~/data/20180719/20180719_drea_si_0_75.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 1.0 -o ~/data/20180719/20180719_drea_si_1_0.csv ~/sim_files


#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.0 -o ~/data/20180719/20180719_drea_ara_0_0.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.0625 -o ~/data/20180719/20180719_drea_ara_0_0625.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.125 -o ~/data/20180719/20180719_drea_ara_0_125.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.25 -o ~/data/20180719/20180719_drea_ara_0_25.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.375 -o ~/data/20180719/20180719_drea_ara_0_375.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.5 -o ~/data/20180719/20180719_drea_ara_0_5.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 0.75 -o ~/data/20180719/20180719_drea_ara_0_75.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ara -t 60 --ar-threshold 1.0 -o ~/data/20180719/20180719_drea_ara_1_0.csv ~/sim_files

#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.0 -o ~/data/20180719/20180719_drea_ar_0_0625.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.0625 -o ~/data/20180719/20180719_drea_ar_0_0625.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.125 -o ~/data/20180719/20180719_drea_ar_0_125.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.25 -o ~/data/20180719/20180719_drea_ar_0_25.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.375 -o ~/data/20180719/20180719_drea_ar_0_375.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.5 -o ~/data/20180719/20180719_drea_ar_0_5.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.75 -o ~/data/20180719/20180719_drea_ar_0_75.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 1.0 -o ~/data/20180719/20180719_drea_ar_1_0.csv ~/sim_files

nice -10 pstn-simulate -s 60 -e arsi -t 60 --seed 1454079265 --ar-threshold 0.5 --si-threshold 0.0 --start-point 4 --stop-point 5 -o $HOME/data/20181118/20181118_dream_0_5__0_0.csv --mit-parse $HOME/mit_dataset/rover_coordination.json
nice -10 pstn-simulate -s 60 -e arsi -t 60 --seed 1454079265 --ar-threshold 0.75 --si-threshold 0.0625 --stop-point 20 -o $HOME/data/20181118/20181118_dream_0_75__0_0625.csv --mit-parse $HOME/mit_dataset/rover_coordination.json
nice -10 pstn-simulate -s 60 -e arsi -t 60 --seed 1454079265 --ar-threshold 1.0 --si-threshold 0.0625 --stop-point 20 -o $HOME/data/20181118/20181118_dream_1_0__0_0625.csv --mit-parse $HOME/mit_dataset/rover_coordination.json
nice -10 pstn-simulate -s 60 -e arsi -t 60 --seed 1454079265 --ar-threshold 0.75 --si-threshold 0.0 --start-point 20 -o $HOME/data/20181118/20181118_dream_0_75__0_0.csv --mit-parse $HOME/mit_dataset/rover_coordination.json
