from __future__ import absolute_import, division, print_function
import numpy as np
import pandas as pd
import scipy.optimize as opt


class read(object):
    """Class for reading data from files"""

    def initial_input_file('init.json'):

    def serpent_output_res ('filename_res.m'):       # Using PyNE parser
    def serpent_composition ('filename.bumat0'):     # Serpent write ready-to-input materials composition after each depletion step. Use it

class write(object):
    def serpent_material_input ('mat.inp'):   #composition only. In main input file "include mat.inp"
    def keff ('keff.m'):               #write K-eff in the file which later could be visualized with PLOTTER in Python (HDF5 format?)
    def spectrum ('spec.m'):           #write Spectrum in the file
    def nuclide_adens (name of nuclide, 'adens_name_of_nuclide.m'):
    def all_cool_constants_for_later_use_in_moltres ('moltres.m'):

class  run(object):
    def rerun_serpent2():

class  plot(object):
    def keff('keff.m'):
    def spectrum('spec.m'):
    def any_table_from_HDF5_data():








