#nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse -o 20181031_rover_dream_0_5__0_0625.csv -e arsi --si-threshold 0.0625 --ar-threshold 0.5 $HOME/mit_dataset/rover_coordination.json
#nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse -o 20181112_rover_srea.csv -e srea $HOME/mit_dataset/rover_coordination.json
nice -10 pstn-simulate -t 40 -s 100 --seed 1719746790 \
  -o 20190318_dream_missing.csv -e arsi --ordering-pairs '[(0.375,0.0), (0.75,0.0), (1.0, 0.375), (1.0, 0.75)]' \
  $HOME/sim_files
