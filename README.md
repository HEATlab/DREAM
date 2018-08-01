# libheat

New version of the robotbrunch codebase.

Requirements (python packages) to run are listed in
[requirements.txt](requirements.txt).


## Documentation
To generate Sphinx autodoc documentation:
1. Go to [docs](docs/)
2. Run `make html`.
3. Open the index now generated at `docs/build/html/index.html` using your
   favourite web browser.

Docstrings follow *Google Docstring Style*, and we use the Sphinx Napolean add-on
to convert between Google style to RST for Sphinx.


## Project Notes
Check out the [IDEAS.md](IDEAS.md) file to see what we have tried.

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
of the code, documentation, or the results gathered.

[1]: https://github.com/CrystalLord/pulp/commit/693ad5d91380aacfe48297ad772c2ae4b248970a
