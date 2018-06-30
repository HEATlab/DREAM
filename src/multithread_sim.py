#!/usr/bin/env python3

import multiprocessing
import argparse

from stntools import STN, load_stn_from_json_file
from montsim import Simulator

def main():
    args = parse_args()

    # Set the random seed
    if args.seed is not None:
        random_seed = int(args.seed)
    else:
        random_seed = None

    stn = load_stn_from_json_file(args.stns)["stn"]
    #stn = STN()

    #stn.add_vertex(0, 0)
    #stn.add_vertex(1, 0)
    #stn.add_vertex(2, 0)
    #stn.add_vertex(3, 0)

    #stn.add_edge(0, 1, 0.0, 1000.0)
    #stn.add_edge(1, 2, 0.0, 1000.0, distribution="Something")
    #stn.add_edge(0, 2, 150.0, 1000.0)
    #stn.add_edge(0, 3, 0.0, 1000.0)

    sim_count = args.samples

    sim_options = {}
    if args.execution == "drea-si":
        sim_options["threshold_si"] = args.threshold
    elif args.execution == "drea-ar":
        print("Here")
        sim_options["threshold_ar"] = args.threshold

    results = multiple_simulations(stn, args.execution, sim_count,
                                   threads=args.threads,
                                   random_seed=random_seed,
                                   sim_options=sim_options)

    print("Robustness of {} ".format(args.stns))
    print(results.count(True)/len(results))

def multiple_simulations(starting_stn, execution_strat,
                         count, threads=1, random_seed=None,
                         sim_options={}):
    # Each thread needs its own simulator, otherwise the progress of one thread
    # can overwrite the progress of another
    tasks = [(Simulator(random_seed), starting_stn, execution_strat,
              sim_options)
             for i in range(count)]
    if threads > 1:
        pool = multiprocessing.Pool(threads)
        response = pool.map(_multisim_thread_helper, tasks)
    else:
        response = list(map(_multisim_thread_helper, tasks))
    return response


def _multisim_thread_helper(tup):
    """ Helper function to allow passing multiple arguments to the simulator.
    """
    simulator = tup[0]
    ans = simulator.simulate(tup[1], tup[2], sim_options=tup[3])
    print(ans)
    print(simulator.get_assigned_times())
    return ans

def parse_args():
    """Parse the program arguments
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-t", "--threads", type=int, default=1)
    parser.add_argument("-s", "--samples", type=int, default=100)
    parser.add_argument("-e", "--execution", type=str, default="early")
    parser.add_argument("--threshold", type=float, default=0.1)
    parser.add_argument("--seed", default=None)
    parser.add_argument("stns", help="The STN JSON files to run on.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
