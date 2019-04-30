# DREAM

Also known as the new version of the "RobotBrunch" codebase from HEATlab.

This is the code is closely tied to the paper:

Abrahams et al. 2019. DREAM: An Algorithm for Mitigating the Overhead of Robust Rescheduling.
In _Proc. of the 29th International Conference on Automated Planning and
Scheduling (ICAPS-2019)_.  A pre-print is available [here](https://www.cs.hmc.edu/HEAT/papers/Abrahams_et_al_ICAPS_2019.pdf).

## Usage and Set Up

Requirements (python packages) to run are listed in
[requirements.txt](requirements.txt).

These can be installed via your standard python3 pip method of `pip install -r requirements.txt`.

Newer versions may be used, but these versions have been selected to work on HMC's shared server, Knuth.


## How to Run the Simulator

Usage

```bash
usage: run_simulator.py [-h] [-v] [-t THREADS] [-s SAMPLES] [-e EXECUTION]
                        [-o OUTPUT] [--ar-threshold AR_THRESHOLD]
                        [--si-threshold SI_THRESHOLD] [--mit-parse]
                        [--seed SEED] [--ordering-pairs ORDERING_PAIRS]
                        [--start-point START_POINT] [--stop-point STOP_POINT]
                        [--no-live]
                        stns [stns ...]
```

You may always use the `--help` option to get a full print out of every option.

How to use DREAM on an PSTN:

```bash
$ python3 run_simulator.py -e arsi -s 100 test_data/two_agent_sync.json
```

The `-e` option sets the execution strategy, and the `-s` sets the number of samples to simulate.

## Documentation
To generate Sphinx autodoc documentation:
1. Go to [docs](docs/)
2. Run `make html`.
3. Open the index now generated at `docs/build/html/index.html` using your
   favourite web browser.

Docstrings follow *Google Docstring Style*, and we use the Sphinx Napolean add-on
to convert between Google style to RST for Sphinx.

## Project Notes
Check out the [IDEAS.md](IDEAS.md) file to see what we (as a lab) have tried.

## Unit Tests
This project supports the unit test module. To run the tests in this project,
use the following shell command.

```bash
$ cd <project_dir>
$ python3 -m unittest  # Auto searches for unit tests in <project_dir>/tests
```

PuLP may give a warning. You can implement Jordan's fix [here][1] in PuLP
itself to remove it.

## Credit
This code is copyright of Harvey Mudd College's HEATlab.

Rewrite Started by: Jordan R. Abrahams (HMC '19)

Original Written by:
* Jeb Brooks
* Emilia Reed
* Alexander Gruver
* Sam Dietrich
* Kyle Lund
* Scott Chow
* Jordan R. Abrahams
* Brenner Ryan
* David A. Chu
* Grace Diehl
* Marina Knittel
* Judy Lin
* Liam Lloyd
* James C. Boerkoel Jr.

Please contact Jordan R. Abrahams if you have any questions about the internals
of the code, documentation, or any of the results gathered.

[1]: https://github.com/CrystalLord/pulp/commit/693ad5d91380aacfe48297ad772c2ae4b248970a
