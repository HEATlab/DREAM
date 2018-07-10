#!/bin/bash
nice -10 ~/libheat/bin/rb-simulate -s 70 -e early -t 60 -o ~/data/20180709/20180709_early.csv ~/sim_files/*/original_1.json ~/sim_files/*/original_2.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e srea -t 60 -o ~/data/20180709/20180709_srea.csv ~/sim_files/*/original_1.json ~/sim_files/*/original_2.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea -t 60 -o ~/data/20180709/20180709_drea.csv ~/sim_files/*/original_1.json ~/sim_files/*/original_2.json

nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-si -t 60 --threshold 0.0 -o ~/data/20180709/20180709_drea_si_0_0.csv ~/sim_files/*/original_1.json 
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-si -t 60 --threshold 0.25 -o ~/data/20180709/20180709_drea_si_0_3.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-si -t 60 --threshold 0.5 -o ~/data/20180709/20180709_drea_si_0_5.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-si -t 60 --threshold 0.75 -o ~/data/20180709/20180709_drea_si_0_7.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-si -t 60 --threshold 1.0 -o ~/data/20180709/20180709_drea_si_1_0.csv ~/sim_files/*/original_1.json

nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-alp -t 60 --threshold 0.0 -o ~/data/20180709/20180709_drea_alp_0_0.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-alp -t 60 --threshold 0.25 -o ~/data/20180709/20180709_drea_alp_0_3.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-alp -t 60 --threshold 0.5 -o ~/data/20180709/20180709_drea_alp_0_5.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-alp -t 60 --threshold 0.75 -o ~/data/20180709/20180709_drea_alp_0_7.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-alp -t 60 --threshold 1.0 -o ~/data/20180709/20180709_drea_alp_1_0.csv ~/sim_files/*/original_1.json

nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-ar -t 60 --threshold 0.0 -o ~/data/20180709/20180709_drea_ar_0_0.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-ar -t 60 --threshold 0.25 -o ~/data/20180709/20180709_drea_ar_0_3.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-ar -t 60 --threshold 0.5 -o ~/data/20180709/20180709_drea_ar_0_5.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-ar -t 60 --threshold 0.75 -o ~/data/20180709/20180709_drea_ar_0_7.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 70 -e drea-ar -t 60 --threshold 1.0 -o ~/data/20180709/20180709_drea_ar_1_0.csv ~/sim_files/*/original_1.json
