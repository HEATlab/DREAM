#!/bin/bash
nice -10 pstn-simulate -s 100 -e early -t 60 -o ~/data/20180712/20180712_early.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e srea -t 60 -o ~/data/20180712/20180712_srea.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea -t 60 -o ~/data/20180712/20180712_drea.csv ~/sim_files

nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.0 -o ~/data/20180712/20180712_drea_si_0_0.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.1 -o ~/data/20180712/20180712_drea_si_0_1.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.2 -o ~/data/20180712/20180712_drea_si_0_2.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.3 -o ~/data/20180712/20180712_drea_si_0_3.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.4 -o ~/data/20180712/20180712_drea_si_0_4.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.5 -o ~/data/20180712/20180712_drea_si_0_5.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 0.75 -o ~/data/2018071/20180712_drea_si_0_75.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-si -t 60 --si-threshold 1.0 -o ~/data/20180712/20180712_drea_si_1_0.csv ~/sim_files

#nice -10 pstn-simulate -s 100 -e drea-alp -t 60 --si-threshold 0.0 -o ~/data/20180712_test/20180712_drea_alp_0_0.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-alp -t 60 --si-threshold 0.25 -o ~/data/20180712_test/20180712_drea_alp_0_3.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-alp -t 60 --si-threshold 0.5 -o ~/data/20180712_test/20180712_drea_alp_0_5.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-alp -t 60 --si-threshold 0.75 -o ~/data/20180712_test/20180712_drea_alp_0_7.csv ~/sim_files
#nice -10 pstn-simulate -s 100 -e drea-alp -t 60 --si-threshold 1.0 -o ~/data/20180712_test/20180712_drea_alp_1_0.csv ~/sim_files

nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-hreshold 0.0 -o ~/data/20180712/20180712_drea_ar_0_0.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-hreshold 0.1 -o ~/data/20180712/20180712_drea_ar_0_1.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-hreshold 0.2 -o ~/data/20180712/20180712_drea_ar_0_2.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-hreshold 0.3 -o ~/data/20180712/20180712_drea_ar_0_3.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-hreshold 0.4 -o ~/data/20180712/20180712_drea_ar_0_4.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.5 -o ~/data/20180712/20180712_drea_ar_0_5.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 0.75 -o ~/data/20180712/20180712_drea_ar_0_7.csv ~/sim_files
nice -10 pstn-simulate -s 100 -e drea-ar -t 60 --ar-threshold 1.0 -o ~/data/20180712/20180712_drea_ar_1_0.csv ~/sim_files
