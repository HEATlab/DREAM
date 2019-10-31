
from libheat import functiontimer
from libheat.srea import srea
from libheat.stntools import load_stn_from_json, mitparser, STN
from libheat.montsim import Simulator
from libheat.dmontsim import DecoupledSimulator
import libheat.printers as pr
import libheat.parseindefinite
from libheat import sim2csv

import glob
import os
import json


MAX_SEED = 2 ** 31 - 1
"""The maximum number a random seed can be."""
DEFAULT_DECOUPLE = "srea"
"""The default decoupling type for DecoupledSimulator"""


def main():
    directory = "dynamically_controllable/"

    data_list = glob.glob(os.path.join(directory, '*.json'))

    counter = 0
    for data in data_list:
        with open(data, 'r') as f:
            stn = load_stn_from_json(f.read(), using_pstn=True)
        inputstn = stn['stn']

        alpha, outputstn = srea(inputstn)
        stnjson = outputstn.for_json()
        with open('srea_output/' + data[len(directory):], 'w') as json_file:
            json.dump(stnjson, json_file)
        print("finished with", data[len(directory):])
        counter += 1
        print("total progress", counter, "out of", len(data_list))




if __name__ == "__main__":
    main()
