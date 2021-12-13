## Scripts
This directory contains various scripts to help you set-up and analyze results
of your SaltProc simulations.

### `xsdata`
The script in this directory downloads and processes the JEFF 
3.1.2 cross section library for running the integration tests 
on a UNIX-like machine. Set the `DATADIR` variable inside 
the script to the directory where you want to store the cross 
section libraries.

To run the script, execute
```
source process_j312.sh
```
