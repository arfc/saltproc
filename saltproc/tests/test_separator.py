from __future__ import absolute_import, division, print_function
from saltproc import Separator
from saltproc import Depcode
import os
import sys
import numpy as np
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
input_file = directory+'/test'

serpent = Depcode(codename='SERPENT',
                  exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
                  template_fname=directory+'/template.inp',
                  input_fname=input_file,
                  iter_matfile=directory+'/material',
                  geo_file=None)

process = Separator(mass_flowrate=10,
                    capacity=99.0,
                    volume=95.0,
                    efficiency="self")


def test_rem_elements():
    mats = serpent.read_dep_comp(input_file, 1)
    waste = process.rem_elements(mats['fuel'])
    np.testing.assert_almost_equal(waste[541350000], 19.704682182207094)
    np.testing.assert_almost_equal(waste[541360000], 175.61778182289143)
    np.testing.assert_almost_equal(waste[541280000], 9.865308312535086e-05)
    np.testing.assert_almost_equal(waste[541390000], 0.026035512575026072)
    np.testing.assert_almost_equal(waste[360790000], 6.420212330439721e-17)
    np.testing.assert_almost_equal(waste[360800000], 1.7247218488207868e-06)
    np.testing.assert_almost_equal(waste[360920000], 0.0002854823675582336)
    np.testing.assert_almost_equal(waste[360860000], 28.127452116170364)
    assert waste.mass == 531.7483879940079
