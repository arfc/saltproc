from __future__ import absolute_import, division, print_function
from saltproc import Separator
from saltproc import DepcodeSerpent
import os
import sys
import numpy as np
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
input_file = directory + '/test'

serpent = DepcodeSerpent(
    exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
    template_path=directory +
    '/template.inp',
    input_path=input_file,
    iter_matfile=directory +
    '/material',
    geo_file=None)

process = Separator(mass_flowrate=10,
                    capacity=99.0,
                    volume=95.0,
                    efficiency="self")


def test_rem_elements():
    mats = serpent.read_dep_comp(input_file, True)
    waste = process.rem_elements(mats['fuel'])
    np.testing.assert_almost_equal(waste[541350000], 19.5320018359295)
    np.testing.assert_almost_equal(waste[541360000], 174.0787699729534)
    np.testing.assert_almost_equal(waste[541280000], 9.778854502227908e-05)
    np.testing.assert_almost_equal(waste[541390000], 0.025807352522232645)
    np.testing.assert_almost_equal(waste[360790000], 1.2668053364239955e-15)
    np.testing.assert_almost_equal(waste[360800000], 1.709607392097611e-06)
    np.testing.assert_almost_equal(waste[360920000], 0.0002829805665329617)
    np.testing.assert_almost_equal(waste[360860000], 27.88095952489617)
    assert waste.mass == 527.0884551454453
