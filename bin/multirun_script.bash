#!/bin/bash
nice -10 ~/libheat/bin/rb-simulate -s 100 -e early -t 60 -o ~/data/20180706/20180706_early.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e srea -t 60 -o ~/data/20180706/20180706_srea.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea -t 60 -o ~/data/20180706/20180706_drea.csv ~/sim_files/*/original_1.json

nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-si -t 60 --threshold 0.0 -o ~/data/20180706/20180706_drea_si_0_0.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-si -t 60 --threshold 0.3 -o ~/data/20180706/20180706_drea_si_0_3.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-si -t 60 --threshold 0.5 -o ~/data/20180706/20180706_drea_si_0_5.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-si -t 60 --threshold 0.7 -o ~/data/20180706/20180706_drea_si_0_7.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-si -t 60 --threshold 1.0 -o ~/data/20180706/20180706_drea_si_1_0.csv ~/sim_files/*/original_1.json

nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-alp -t 60 --threshold 0.0 -o ~/data/20180706/20180706_drea_alp_0_0.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-alp -t 60 --threshold 0.3 -o ~/data/20180706/20180706_drea_alp_0_3.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-alp -t 60 --threshold 0.5 -o ~/data/20180706/20180706_drea_alp_0_5.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-alp -t 60 --threshold 0.7 -o ~/data/20180706/20180706_drea_alp_0_7.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-alp -t 60 --threshold 1.0 -o ~/data/20180706/20180706_drea_alp_1_0.csv ~/sim_files/*/original_1.json

nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-ar -t 60 --threshold 0.0 -o ~/data/20180706/20180706_drea_ar_0_0.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-ar -t 60 --threshold 0.3 -o ~/data/20180706/20180706_drea_ar_0_3.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-ar -t 60 --threshold 0.5 -o ~/data/20180706/20180706_drea_ar_0_5.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 100 -e drea-ar -t 60 --threshold 0.7 -o ~/data/20180706/20180706_drea_ar_0_7.csv ~/sim_files/*/original_1.json
nice -10 ~/libheat/bin/rb-simulate -s 150 -e drea-ar -t 60 --threshold 1.0 -o ~/data/20180706/20180706_drea_ar_1_0.csv ~/sim_files/*/original_1.json
