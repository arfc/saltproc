## SaltProc

[![Build Status](https://travis-ci.org/andrewryh/saltproc.svg?branch=develop)](https://travis-ci.org/andrewryh/saltproc)

The SaltProc is a fuel reprocessing simulation tool for liquid fueled nuclear
reactors.

How to run SaltProc:

cd /path/to/saltproc
python run_saltproc.py -n 4 -d 1 -i examples/tap_main.json
```
-n          number of cluster nodes to use in Serpent
-d          number of threads to use in Serpent
-i          path and name of SaltProc main input file
```

### Installation

Detailed installation instructions can be found in the
[User's Guide](https://arfc.github.io/saltproc/installation.html).

### Documentation

The documentation for SaltProc can be found at
[arfc.github.io/saltproc/](http://arfc.github.io/saltproc/).
The entire contents of that
website can be built from the `doc` directory in the repositiory using the following steps with the [`conda`](https://docs.conda.io/en/latest/) tool:

1. `conda env create -f doc/doc-environment.yml`
2. `cd doc/`
3. `make clean`
4. `make html`

After these steps, the website will be found in `saltproc/doc/_build/html`.

_Note_: We recommend using [`mamba`](https://github.com/mamba-org/mamba) CLI tool to install packages quickly. SaltProc has a compltex package dependency structure which can result is long environment solve times in the default ``conda`` solver. ``mamba`` is a reimplementation of ``conda`` in ``C++`` and we have found it is significantly faster.


## License

The license for this work can be found
[here](https://github.com/arfc/saltproc/blob/master/LICENSE). Please
be respectful of my intellectual work by communicating with me about its use,
understanding its limitations, and citing me where appropriate. We would be
thrilled to work with you on improving it.


## Contribution

This repository is a work in progress. We would love it if you wanted to
contribute to this code here in this repository. [Here is some information about
how to do that.](https://github.com/arfc/saltproc/blob/master/CONTRIBUTING.md).
