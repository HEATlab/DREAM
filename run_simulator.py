#!/usr/bin/env python3

"""
This program runs multiple Monte-Carlo simulations for a given execution
strategy.


"""
import os
import os.path
import sys
import time
import multiprocessing
import argparse
import numpy as np


from libheat import functiontimer
from libheat.stntools import STN, load_stn_from_json_file
from libheat.montsim import Simulator
from libheat.dmontsim import DecoupledSimulator
import libheat.printers as pr
from libheat import sim2csv


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
    sim_options["ar_threshold"] = args.ar_threshold
    sim_options["alp_threshold"] = args.si_threshold
    sim_options["si_threshold"] = args.si_threshold

    # simulate across multiple paths.
    stn_paths = folder_harvest(args.stns, recurse=True, only_json=True)
    across_paths(stn_paths, args.execution, args.threads, sim_count,
                 sim_options,
                 output=args.output,
                 live_updates=(not args.no_live),
                 random_seed=random_seed)


def across_paths(stn_paths, execution, threads, sim_count, sim_options,
                 output=None, live_updates=True, random_seed=None):
    """Runs multiple simulations for each STN in the provided iterable.

    Args:
        stn_paths (iterable): iterable (like a List) of strings.
        execution (str): Execution strategy to use on each STN.
        threads (int): Number of threads to use.
        sim_count (int): Number of simulations (samples) to use.
        sim_options (dict): Dictionary of simulation options to use.
        output (str, optional): Output file path. Default no output.
        live_updates (boolean, optional): Whether to provide live updates.
        random_seed (int, optional): The random seed to start out with,
            defaults to a random... random seed.
    """
    num_paths = len(stn_paths)
    for i, path in enumerate(stn_paths):
        stn = load_stn_from_json_file(path)["stn"]

        start_time = time.time()
        response_dict = multiple_simulations(stn, execution, sim_count,
                                             threads=threads,
                                             random_seed=random_seed,
                                             sim_options=sim_options)
        runtime = time.time() - start_time

        results = response_dict["sample_results"]
        reschedules = response_dict["reschedules"]
        sent_schedules = response_dict["sent_schedules"]

        robustness = results.count(True)/len(results)
        vert_count = len(stn.verts)
        cont_dens = len(stn.contingent_edges)/len(stn.edges)
        synchrony = len(stn.interagent_edges)/len(stn.edges)

        total_sd = 0
        for e in stn.contingent_edges.values():
            total_sd += e.sigma
        sd_avg = total_sd / len(stn.contingent_edges)

        results_dict = {}
        results_dict["execution"] = execution
        results_dict["robustness"] = robustness
        results_dict["threads"] = threads
        results_dict["random_seed"] = random_seed
        results_dict["runtime"] = runtime
        results_dict["samples"] = sim_count
        results_dict["timestamp"] = time.time()
        results_dict["stn_path"] = path
        results_dict["ar_threshold"] = sim_options["ar_threshold"]
        results_dict["si_threshold"] = sim_options["si_threshold"]
        results_dict["synchronous_density"] = synchrony
        results_dict["sd_avg"] = sd_avg
        results_dict["vert_count"] = vert_count
        results_dict["contingent_density"] = cont_dens
        results_dict["reschedule_freq"] = sum(reschedules)/len(reschedules)
        results_dict["send_freq"] = sum(sent_schedules)/len(sent_schedules)

        if output is not None:
            sim2csv.save_csv_row(results_dict, output)

        if live_updates:
            _print_results(results_dict, i + 1, num_paths)


def _print_results(results_dict, i, num_paths):
    """Pretty print the results of N samples of simulation"""
    print("-"*79)
    print("    Ran on: {}".format(results_dict["stn_path"]))
    print("    Timestamp: {}".format(results_dict["timestamp"]))
    print("    Samples: {}".format(results_dict["samples"]))
    print("    Threads: {}".format(results_dict["threads"]))
    print("    Execution: {}".format(results_dict["execution"]))
    print("    AR Threshold: {}".format(results_dict["ar_threshold"]))
    print("    SI Threshold: {}".format(results_dict["si_threshold"]))
    print("    Robustness: {}".format(results_dict["robustness"]))
    print("    Seed: {}".format(results_dict["random_seed"]))
    print("    Runtime: {}".format(results_dict["runtime"]))
    print("    Vert Count: {}".format(results_dict["vert_count"]))
    print("    Cont Edge Dens: {}".format(results_dict["contingent_density"]))
    print("    Cont SD Avg: {}".format(results_dict["sd_avg"]))
    print("    Sync Density: {}".format(results_dict["synchronous_density"]))
    print("    Resc Freq: {}".format(results_dict["reschedule_freq"]))
    print("    Send Freq: {}".format(results_dict["send_freq"]))
    print("    Total Progress: {}/{}".format(i, num_paths))
    print("-"*79)


def multiple_simulations(starting_stn, execution_strat,
                         count, threads=1, random_seed=None,
                         sim_options={}):
    # Each thread needs its own simulator, otherwise the progress of one thread
    # can overwrite the progress of another
    print("Random seed is: {}".format(random_seed))
    if random_seed is not None:
        seed_gen = np.random.RandomState(random_seed)
        seeds = [seed_gen.randint(MAX_SEED) for i in range(count)]
        if execution_strat == "da":
            tasks = [(DecoupledSimulator(seeds[i]), starting_stn,
                      execution_strat,
                      sim_options)
                     for i in range(count)]
        else:
            tasks = [(Simulator(seeds[i]), starting_stn, execution_strat,
                      sim_options)
                     for i in range(count)]
    else:
        if execution_strat == "da":
            tasks = [(DecoupledSimulator(None), starting_stn, execution_strat,
                      sim_options)
                     for i in range(count)]
        else:
            tasks = [(Simulator(None), starting_stn, execution_strat,
                      sim_options)
                     for i in range(count)]
    if threads > 1:
        print("Using multithreading; threads = {}".format(threads))
        try_count = 0
        while try_count <= 3:
            try_count += 1
            response = None
            try:
                with multiprocessing.Pool(threads) as pool:
                    response = pool.map(_multisim_thread_helper, tasks)
                break
            except BlockingIOError:
                pr.warning("Got BlockingIOError; attempting to remake threads")
                pr.warning("Retrying in 3 seconds...")
                time.sleep(3.0)
                pr.warning("Retrying now")

    else:
        print("Using single thread; threads = {}".format(threads))
        response = list(map(_multisim_thread_helper, tasks))

    # Unzip each of the response values.
    sample_results = [r[0] for r in response]
    reschedules = [r[1] for r in response]
    sent_schedules = [r[2] for r in response]
    # Package the response into a nice dict to send back.
    response_dict = {"sample_results": sample_results, "reschedules":
                     reschedules, "sent_schedules": sent_schedules}
    return response_dict


def _multisim_thread_helper(tup):
    """ Helper function to allow passing multiple arguments to the simulator.
    """
    simulator = tup[0]
    if tup[2] == "da":
        ans = simulator.simulate(tup[1], sim_options=tup[3])
    else:
        ans = simulator.simulate(tup[1], tup[2], sim_options=tup[3])
    reschedule_count = simulator.num_reschedules
    sent_count = simulator.num_sent_schedules
    pr.verbose("Assigned Times: {}".format(simulator.get_assigned_times()))
    pr.verbose("Successful?: {}".format(ans))
    return ans, reschedule_count, sent_count


def folder_harvest(folder_paths: list, recurse=True, only_json=True) -> list:
    """ Retrieves a list of STN filepaths given a list of folderpaths.

    Args:
        folder_paths (list): List of strings that represent file/folder paths.
        recursive (:obj:bool, optional): Boolean indicating whether to recurse
            into directories.
    Returns:
        Returns a flat list of STN paths.
    """
    stn_files = []
    for folder_path in folder_paths:
        if os.path.isfile(folder_path):
            # Folder was actually a stn file. Just append it.
            if only_json:
                _, ext = os.path.splitext(folder_path)
                if ext == ".json":
                    stn_files.append(folder_path)
            else:
                stn_files.append(folder_path)
        elif os.path.isdir(folder_path):
            # This was actually a folder this time!
            contents = os.listdir(folder_path)
            for c in contents:
                # Make sure to include the folder path
                long_path = folder_path + "/" + c
                if os.path.isfile(long_path):
                    if only_json:
                        _, ext = os.path.splitext(long_path)
                        if ext == ".json":
                            stn_files.append(long_path)
                    else:
                        stn_files.append(long_path)
                elif os.path.isdir(long_path) and recurse:
                    stn_files += folder_harvest([long_path], recurse=True)
                else:
                    # This should never happen, but maybe?
                    pr.warning("STN path was not file or directory: " +
                               folder_path)
                    pr.warning("Skipping...")
        else:
            # This should never happen, but maybe?
            pr.warning("STN path was not file or directory: " +
                       folder_path)
            pr.warning("Skipping...")
    return stn_files


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
    parser.add_argument("--ar-threshold", type=float, default=0.0,
                        help="AR Threshold to use for AR and ARSI")
    parser.add_argument("--si-threshold", type=float, default=0.0,
                        help="SI Threshold to use for SI, ALP and ARSI")
    parser.add_argument("--seed", default=None, help="Set the random seed")
    parser.add_argument("--no-live", action="store_true",
                        help="Turn off live update printing")
    parser.add_argument("stns", help="The STN JSON files to run on.",
                        nargs="+")
    return parser.parse_args()


if __name__ == "__main__":
    main()
    print(functiontimer.get_times())
