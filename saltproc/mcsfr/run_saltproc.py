import math
import itertools
import subprocess
import os
import numpy as np
import sys
import h5py
import shutil
import argparse
sys.path.append(os.path.abspath('..'))
from saltproc import saltproc

##############################################################
######### THIS IS THE INPUT FILE SECTION OF SALTPROC #########
######### TO RUN, simply set these settings and run  #########
##############################################################
#########         `python run_saltproc.py            #########
##############################################################

# SERPENT input file
input_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(input_path)
print(input_path)
input_file = os.path.join(input_path, 'mcsfr_design3.inp')
# desired database file name
db_file = os.path.join(input_path, 'mcsfr.hdf5')
# material file with fuel composition and density
mat_file = os.path.join(input_path, 'iter_mat_file')

init_mat_file = os.path.join(input_path, 'mat_composition3.inp')

# executable path of Serpent
exec_path = '/projects/sciteam/bahg/serpent30/src/sss2'

# Number of cores and nodes to use in cluster
cores = 32
nodes = 4

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

driver_vol = 38*10 ^ 3
blanket_vol = 75*10 ^ 3


# reprocessing scheme defined by user
# key: group name
# value: dictionary:
#   key: element : list of elements to be reprocessed
#        freq: frequency of processing (negative value => process every timestep) (default = -1)
#        qty: quantity of processing [kg/freq] (negative value -> all for removal, fill up for adding) (default = -1)
#        comp: (only for adding) isotopic of input material
#        begin_time: start removing at timestep (negative -> start from the beginning) (default -1)
#        end_time: stop removing at timestep (default 1e299)
#        from: material to process from (default 'fertile')
#        to material to process to (default 'waste')
#        eff: efficiency of reprocessing (default 1)

rep_scheme = {'volatile_gases': {'element': ['Kr', 'Xe', 'Ar', 'Ne', 'H', 'N', 'O', 'Rn'],
                                 'from': driver_mat_name},
              'noble_metals': {'element': ['Se', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
                                           'Ag', 'Sb', 'Te', 'Zr', 'Cd', 'In', 'Sn'],
                               'from': driver_mat_name},
              'rare_earths': {'element': ['Y', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm',
                                          'Gd', 'Eu', 'Dy', 'Ho', 'Er', 'Tb', 'Ga',
                                          'Ge', 'As', 'Zn'],
                              'from': driver_mat_name},
              'feed_driver': {'element': ['U238', 'U235'],
                              'comp': [99.7, 0.3],
                              'to': driver_mat_name},
              'feed_blanket': {'element': ['U238', 'U235'],
                               'comp': [99.7, 0.3],
                               'to': blanket_mat_name},
              'pu': {'element': ['Pu'],
                     'from': blanket_mat_name,
                     'to': driver_mat_name}
              }

###############################################################
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
    if not two_region:
        blanket_mat_name = ''
        blanket_vol = 0

    run = saltproc(steps=steps, cores=cores, nodes=nodes,
                   bw=bw, exec_path=exec_path, restart=restart,
                   input_file=input_file,
                   mat_file=mat_file, init_mat_file=init_mat_file,
                   driver_mat_name=driver_mat_name,
                   blanket_mat_name=blanket_mat_name,
                   driver_vol=driver_vol, blanket_vol=blanket_vol,
                   rep_scheme=rep_scheme)
    run.main()
