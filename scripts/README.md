## Scripts
This directory contains various scripts to help you set-up and analyze results
of your SaltProc simulations.

### `xsdata`
The scripts in this directory downloads and processes cross sections data for
use in Serpent and OpenMC

#### `process_jeff312.bash`
Downloads and processes the JEFF 3.1.2 cross section library -- as well as
spontaneous and delayed fission neutron and
decay data -- for running the integration tests 
on a UNIX-like machine.

By default, the script will only download the thermal and 900K 
cross section libraries. If you want data at more temperatures,
you can add them to ``TEMPS`` array in the script. *The temperatures
in the array must be available for the JEFF 3.1.2 library*. Alternativley,
you can uncomment the ``TEMPS`` declaration on line 13 in the script,
which will download and process the libraries at all available temperatures.

To run the script, execute
```
XSDIR=[PATH TO XSDIR] bash process_j312.bash
```

Where `XSDIR` is a path to the directory where you want to store the cross 
section libraries. Running the script without setting `XSDIR` will install the cross section library in the current working directory.


#### `download_endfb71.bash`
Downloads and processes the endfb7x incident neutron data, and 
ENDFB71 thermal scattering data in ACE format-- as well as
spontaneous and delayed fission neutron and
decay data -- for running Serpent models
on a UNIX-like machine.

To run the script, execute
```
XSDIR=[PATH TO XSDIR] bash download_endfb71.bash
```

Where `XSDIR` is a path to the directory where you want to store the cross 
section libraries. Running the script without setting `XSDIR` will install the cross section library in the current working directory.

#### `process_endfb71_to_openmc.bash`
Processes the endfb71 library created by the previous script into
OpenMC's HDF5 format for cross section data on a UNIX-like machine.

*You must have installed OpenMC on your machine and have openmc repo on your
machine in order for this script to work*
Information about how to do this can be found [here](https://docs.openmc.org/en/latest/usersguide/install.html).

To run the script, execute
```
XSDIR=[PATH TO XSDIR] $OPENMC_ENV=[NAME OF OPENMC CONDA ENVIRONMENT] $OPENMC_DIR=[PATH TO OPENMC REPO] bash download_endfb71.bash
```

Where `XSDIR` is a path to the directory where you want to store the cross 
section libraries. Running the script without setting `XSDIR` will install the cross section library in the current working directory.
