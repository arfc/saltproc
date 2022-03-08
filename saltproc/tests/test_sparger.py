from __future__ import absolute_import, division, print_function
from saltproc import Sparger
from saltproc import DepcodeSerpent
import os
import sys
import numpy as np
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
iter_inputfile = directory + '/test'

serpent = DepcodeSerpent(
    exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
    template_inputfiles_path=directory +
    '/template.inp',
    geo_files=None)

serpent.iter_inputfile = iter_inputfile
serpent.iter_matfile = directory + '/material'

process = Sparger(mass_flowrate=10,
                  capacity=99.0,
                  volume=95.0,
                  efficiency="self")


def test_rem_elements():
    mats = serpent.read_dep_comp(True)
    waste = process.rem_elements(mats['fuel'])
    np.testing.assert_almost_equal(waste[541350000], 8.061014535231715)
    np.testing.assert_almost_equal(waste[541360000], 71.8437109936129)
    np.testing.assert_almost_equal(waste[541280000], 4.0358120454079906e-05)
    np.testing.assert_almost_equal(waste[541390000], 0.010650902326605592)
    np.testing.assert_almost_equal(waste[360790000], 6.420212330439721e-17)
    np.testing.assert_almost_equal(waste[360800000], 7.029023635956131e-07)
    np.testing.assert_almost_equal(waste[360920000], 0.00011634701042301513)
    np.testing.assert_almost_equal(waste[360860000], 11.463212220507412)
    assert waste.mass == 217.43479356542446
