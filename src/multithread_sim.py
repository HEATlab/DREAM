#!/usr/bin/env python3

import time
import multiprocessing
import argparse
import numpy as np


from stntools import STN, load_stn_from_json_file
from montsim import Simulator
import printers as pr

MAX_SEED = 2**32

def main():
    args = parse_args()

    # Set the random seed
    if args.seed is not None:
        random_seed = int(args.seed)
    else:
        random_seed = np.random.randint(MAX_SEED)

    stn = load_stn_from_json_file(args.stns)["stn"]

    if args.verbose:
        pr.set_verbosity(1)
        pr.verbose("Verbosity Set")

    sim_count = args.samples

    sim_options = {}
    if args.execution == "drea-si":
        sim_options["threshold_si"] = args.threshold
    elif args.execution == "drea-ar":
        print("Here")
        sim_options["threshold_ar"] = args.threshold

    start_time = time.time()
    results = multiple_simulations(stn, args.execution, sim_count,
                                   threads=args.threads,
                                   random_seed=random_seed,
                                   sim_options=sim_options)
    run_time = time.time() - start_time

    robustness = results.count(True)/len(results)
    print_results(args.stns, sim_count, run_time, args.execution, robustness,
                  random_seed)

def print_results(stn_path, samples, run_time, execution, robustness, seed):
    print("-"*79)
    print("    Ran on: {}".format(stn_path))
    print("    Samples: {}".format(samples))
    print("    Execution: {}".format(execution))
    print("    Robustness: {}".format(robustness))
    print("    Seed: {}".format(seed))
    print("    Time: {}".format(run_time))
    print("-"*79)


def multiple_simulations(starting_stn, execution_strat,
                         count, threads=1, random_seed=None,
                         sim_options={}):
    # Each thread needs its own simulator, otherwise the progress of one thread
    # can overwrite the progress of another
    if random_seed is not None:
        seed_gen = np.random.RandomState(random_seed)
        seeds = [seed_gen.randint(0, MAX_SEED) for i in range(count)]
        tasks = [(Simulator(seeds[i]), starting_stn, execution_strat,
                  sim_options)
                 for i in range(count)]
    else:
        tasks = [(Simulator(None), starting_stn, execution_strat,
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
    pr.verbose("Assigned Times: {}".format(simulator.get_assigned_times()))
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
