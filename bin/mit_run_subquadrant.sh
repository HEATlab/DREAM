#nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse -o 20181031_rover_dream_0_5__0_0625.csv -e arsi --si-threshold 0.0625 --ar-threshold 0.5 $HOME/mit_dataset/rover_coordination.json
#nice -15 pstn-simulate -t 60 -s 50 --seed 1719746790 --mit-parse -o 20181112_rover_srea.csv -e srea $HOME/mit_dataset/rover_coordination.json
nice -15 pstn-simulate -t 60 -s 50 --seed 1319756710 --mit-parse \
  -o 20190309_rover_dream_quad_indefinite.csv -e arsi --ordering-pairs '[(0.5, 0.5)(0.5, 0.6125)(0.5, 0.725)(0.5, 0.8625)(0.5, 1.0)(0.6125, 0.5)(0.6125, 0.6125)(0.6125, 0.725)(0.6125, 0.8625)(0.6125, 1.0)(0.725, 0.5)(0.725, 0.6125)(0.725, 0.725)(0.725, 0.8625)(0.725, 1.0)(0.8625, 0.5)(0.8625, 0.6125)(0.8625, 0.725)(0.8625, 0.8625)(0.8625, 1.0)(1.0, 0.5)(1.0, 0.6125)(1.0, 0.725)(1.0, 0.8625)(1.0, 1.0)]' \
  $HOME/mit_dataset/rover_coordination.json
