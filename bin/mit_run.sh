#nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse -o 20181031_rover_dream_0_5__0_0625.csv -e arsi --si-threshold 0.0625 --ar-threshold 0.5 $HOME/mit_dataset/rover_coordination.json
#nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse -o 20181112_rover_srea.csv -e srea $HOME/mit_dataset/rover_coordination.json
nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse \
  -o 20190112_rover_drea_indefinite.csv -e arsi --ordering-pairs '[(0.0, 0.0)(0.0, 0.0625)(0.0, 0.125)(0.0, 0.25)(0.0, 0.5)(0.0, 1.0)(0.0625, 0.0)(0.0625, 0.0625)(0.0625, 0.125)(0.0625, 0.25)(0.0625, 0.5)(0.0625, 1.0)(0.125, 0.0)(0.125, 0.0625)(0.125, 0.125)(0.125, 0.25)(0.125, 0.5)(0.125, 1.0)(0.25, 0.0)(0.25, 0.0625)(0.25, 0.125)(0.25, 0.25)(0.25, 0.5)(0.25, 1.0)(0.5, 0.0)(0.5, 0.0625)(0.5, 0.125)(0.5, 0.25)(0.5, 0.5)(0.5, 1.0)(1.0, 0.0)(1.0, 0.0625)(1.0, 0.125)(1.0, 0.25)(1.0, 0.5)(1.0, 1.0)]' \
  $HOME/mit_dataset/rover_coordination.json
