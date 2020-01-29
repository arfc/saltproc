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

Installing SaltProc from source is a two-step process. First, clone the source
code from GitHub:

	git clone https://github.com/arfc/saltproc.git

Then run the following commands from the unzipped directory:

	cd saltproc/
	python setup.py install --user

Detailed installation instructions can be found in the
[User's Guide](https://arfc.github.io/saltproc/installation.html).

### Documentation

The documentation for SaltProc can be found at
[arfc.github.io/saltproc/](http://arfc.github.io/saltproc/).
Additionally, the entire contents of that
website can be built from the doc directory in the source code using the
following steps

1. `pip install sphinx`
2. `pip install sphinx_rtd_theme`.
3. `cd doc/`
4. `sphinx-apidoc --separate --force --output-dir=src/ ../saltproc`
5. `make clean`
6. `make html`

After these steps, the website will be found in `saltproc/doc/_build/html`.

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

## Other

- You will find the current state of the test suite on our [Travis continuous
integration servers](https://travis-ci.org/arfc/saltproc).
