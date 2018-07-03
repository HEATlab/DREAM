#!/usr/bin/env python3

"""
This program runs multiple Monte-Carlo simulations for a given execution
strategy.


"""

import time
import multiprocessing
import argparse
import numpy as np


from stntools import STN, load_stn_from_json_file
from montsim import Simulator
import printers as pr
import sim2csv


MAX_SEED = 2**32


def main():
    args = parse_args()

    # Set the random seed
    if args.seed is not None:
        random_seed = int(args.seed)
    else:
        random_seed = np.random.randint(MAX_SEED)

    if args.verbose:
        pr.set_verbosity(1)
        pr.verbose("Verbosity set to: 1")

    sim_count = args.samples

    sim_options = {}
    if args.execution == "drea-si":
        sim_options["threshold_si"] = args.threshold
    elif args.execution == "drea-ar":
        sim_options["threshold_ar"] = args.threshold

    # simulate across multiple paths.
    across_paths(args.stns, args.execution, args.threads, sim_count,
                 sim_options,
                 output=args.output,
                 live_updates=(not args.no_live),
                 random_seed=random_seed)


def across_paths(stn_paths, execution, threads, sim_count, sim_options,
                 output=None, live_updates=True, random_seed=None):
    """
    Runs multiple simulations for each STN in the provided iterable.

    Args:
        stn_paths:
    """
    num_paths = len(stn_paths)
    for i, path in enumerate(stn_paths):
        stn = load_stn_from_json_file(path)["stn"]

        start_time = time.time()
        results = multiple_simulations(stn, execution, sim_count,
                                       threads=threads,
                                       random_seed=random_seed,
                                       sim_options=sim_options)
        runtime = time.time() - start_time

        robustness = results.count(True)/len(results)

        results_dict = {}
        results_dict["execution"] = execution
        results_dict["robustness"] = robustness
        results_dict["threads"] = threads
        results_dict["random_seed"] = random_seed
        results_dict["runtime"] = runtime
        results_dict["samples"] = sim_count
        results_dict["stn_path"] = path
        results_dict["synchronous_density"] = "placeholder"
        results_dict["reschedule_freq"] = "placeholder"

        if output is not None:
            sim2csv.save_csv_row(results_dict, output)

        if live_updates:
            _print_results(results_dict, i + 1, num_paths)


def _print_results(results_dict, i, num_paths):
    print("-"*79)
    print("    Ran on: {}".format(results_dict["stn_path"]))
    print("    Samples: {}".format(results_dict["samples"]))
    print("    Threads: {}".format(results_dict["threads"]))
    print("    Execution: {}".format(results_dict["execution"]))
    print("    Robustness: {}".format(results_dict["robustness"]))
    print("    Seed: {}".format(results_dict["random_seed"]))
    print("    Runtime: {}".format(results_dict["runtime"]))
    print("    Sync Density: {}".format(results_dict["synchronous_density"]))
    print("    Resc. Freq: {}".format(results_dict["reschedule_freq"]))
    print("    Total Progress: {}/{}".format(i, num_paths))
    print("-"*79)


def multiple_simulations(starting_stn, execution_strat,
                         count, threads=1, random_seed=None,
                         sim_options={}):
    # Each thread needs its own simulator, otherwise the progress of one thread
    # can overwrite the progress of another
    if random_seed is not None:
        seed_gen = np.random.RandomState(random_seed)
        seeds = [seed_gen.randint(MAX_SEED) for i in range(count)]
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
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Turns on more printing")
    parser.add_argument("-t", "--threads", type=int, default=1,
                        help="Number of system threads to use. Default is 1.")
    parser.add_argument("-s", "--samples", type=int, default=100,
                        help="Number of Monte-Carlo samples to use, default"
                        " is 100")
    parser.add_argument("-e", "--execution", type=str, default="early",
                        help="Set the execution strategy to use. Default is"
                        " 'early'")
    parser.add_argument("-o", "--output", type=str,
                        help="Write the simulation results to a CSV.")
    parser.add_argument("--threshold", type=float, default=0.1)
    parser.add_argument("--seed", default=None, help="Set the random seed")
    parser.add_argument("--no-live", action="store_true",
                        help="Turn off live update printing")
    parser.add_argument("stns", help="The STN JSON files to run on.",
                        nargs="+")
    return parser.parse_args()


if __name__ == "__main__":
    main()
