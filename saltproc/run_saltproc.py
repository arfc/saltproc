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

##############################################################
######### THIS IS THE INPUT FILE SECTION OF SALTPROC #########
######### TO RUN, simply set these settings and run  #########
##############################################################
#########         `python run_saltproc.py            #########
##############################################################

# SERPENT input file
input_file = 'core'
# desired database file name
db_file = 'db_saltproc.hdf5'
# material file with fuel composition and density
mat_file = 'fuel_comp'

# executable path of Serpent
exec_path = '/projects/sciteam/bahg/serpent30/src/sss2'

# Number of cores and nodes to use in cluster
cores = 32
nodes = 32

# timesteps of 3 days of run Saltproc
# total days = (3 * steps) [days]
steps = 5

# True: restart by reading from a previously existing database.
#       Length of new database would be (previous databse + steps)
# False: Start from timestep zero.
restart = False

# True: Uses blue water command (aprun) to run SERPERNT
# False: Simply runs the executable command
bw = False


parser = argparse.ArgumentParser()
parser.add_argument('-r', choices=['True', 'False'], default=restart) # restart flag -r 
parser.add_argument('-n', nargs=1, type=int, default=nodes) # number of nodes
parser.add_argument('-steps', nargs=1, type=int, default=steps) # steps for depletion
parser.add_argument('-bw', choices=['True', 'False'], default=bw) # blue waters?

args = parser.parse_args()
restart = bool(args.r)
nodes = int(args.n)
steps = int(args.steps)
bw = bool(args.bw)


#########           END OF INPUT FILE SECTION         #########
###############################################################


if __name__ == "__main__":
    print('Initiating Saltproc:\n'
          '\tRestart = ' + str(restart) + '\n'
          '\tNodes = ' + str(nodes) + '\n'
          '\tCores = ' + str(cores) + '\n'
          '\tSteps = ' + str(steps) + '\n'
          '\tBlue Waters = ' + str(bw) + '\n'
          '\tSerpent Path = ' + exec_path + '\n'
          '\tInput File Path = ' + input_file + '\n'
          '\tMaterial File Path = ' + mat_file + '\n'
          '\tOutput DB File Path = ' + db_file + '\n'
          )
    # run saltproc
    run = saltproc(steps=steps, cores=cores, nodes=nodes,
                   bw=bw, exec_path=exec_path, restart=restart,
                   input_file=input_file, db_file=db_file, mat_file=mat_file)
    run.main()
