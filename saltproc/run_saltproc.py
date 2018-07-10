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
from two_region import saltproc_two_region
from pyne import serpent
from pyne import nucname

##############################################################
######### THIS IS THE INPUT FILE SECTION OF SALTPROC #########
######### TO RUN, simply set these settings and run  #########
##############################################################
#########         `python run_saltproc.py            #########
##############################################################

# SERPENT input file
input_file = 'mcsfr_design3.inp'
# desired database file name
db_file = 'db_saltproc.hdf5'
# material file with fuel composition and density 
mat_file = 'mat_composition3'

# executable path of Serpent
exec_path = '/projects/sciteam/bahg/serpent30/src/sss2'

# Number of cores and nodes to use in cluster
cores = 32
nodes = 9

# timesteps of 3 days of run Saltproc
# total days = (3 * steps) [days] 
steps = 3

# True: restart by reading from a previously existing database.
#       Length of new database would be (previous databse + steps)
# False: Start from timestep zero.
restart = False

# True: Uses blue water command (aprun) to run SERPERNT
# False: Simply runs the executable command
bw = True


# two region parameters
two_region = True
driver_mat_name = 'fuel'
blanket_mat_name = 'blank'

###############################################################
#########           END OF INPUT FILE SECTION         #########
###############################################################


if __name__ == "__main__":
    # run saltproc
    if two_region:
        run = saltproc_two_region(steps=steps, cores=cores, nodes=nodes,
                                  bw=bw, exec_path=exec_path, restart=restart,
                                  input_file=input_file, db_file=db_file,
                                  mat_file=mat_file, driver_mat_name=driver_mat_name,
                                  blanket_mat_name=blanket_mat_name)
    else:
        run = saltproc(steps=steps, cores=cores, nodes=nodes,
                       bw=bw, exec_path=exec_path, restart=restart,
                       input_file=input_file, db_file=db_file, mat_file=mat_file)
    run.main()
