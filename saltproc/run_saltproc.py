import math
import itertools
import subprocess
import os
import numpy as np
import sys
import h5py
import shutil
import argparse
from saltproc import saltproc
from pyne import serpent
from pyne import nucname


# manually hard-code parameters.
# these are default values
input_file = 'core'
db_file = 'db_saltproc.hdf5'
mat_file = 'fuel_comp'
bw       = False
restart = 'False'
cores = 32
# Parse flags
# Read run command
parser = argparse.ArgumentParser()
parser.add_argument('-r', choices=['True', 'False'])  # Restart flag -r
parser.add_argument(
    '-n',
    nargs=1,
    type=int,
    default=1)         # Number of nodes -n
parser.add_argument(
    '-steps',
    nargs=1,
    type=int,
    default=5)     # Number of steps
parser.add_argument('-bw', choices=['True', 'False'])  # -bw Blue Waters?
args = parser.parse_args()
restart = args.r
nodes = int(args.n[0])
steps = int(args.steps[0])
bw = bool(args.bw)


if __name__ == "__main__":
    # run saltproc
    run = saltproc(steps=steps, cores=cores, nodes=nodes,
                   bw=bw, restart=restart, input_file=input_file,
                   db_file=db_file, mat_file=mat_file)
    run.main()
