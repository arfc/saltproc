## Scripts
This directory contains various scripts to help you set-up and analyze results
of your SaltProc simulations.

### `xsdata`
The script in this directory downloads and processes the JEFF 
3.1.2 cross section library -- as well as spontaneous and delayed fission neutron and
decay data -- for running the integration tests 
on a UNIX-like machine. Set the `DATADIR` variable inside 
the script to the directory where you want to store the cross 
section libraries.

By default, the script will only download the thermal and 900K 
cross section libraries. If you want data at more temperatures,
you can add them to ``TEMPS`` array in the script. *The temperatures
in the array must be available for the JEFF 3.1.2 library*. Alternativley,
you can uncomment the ``TEMPS`` declaration on line 13 in the script,
which will download and process the libraries at all available temperatures.

To run the script, execute
```
source process_j312.bash
```
