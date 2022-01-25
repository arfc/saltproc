from __future__ import absolute_import, division, print_function
from saltproc import Process
from saltproc import DepcodeSerpent
import os
import sys
import numpy as np
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
iter_input_file = directory + '/test'

serpent = DepcodeSerpent(
    exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
    template_path=directory +
    '/template.inp',
    iter_input_file=iter_input_file,
    iter_matfile=directory +
    '/material',
    geo_files=None)

process = Process(mass_flowrate=10,
                  capacity=99.0,
                  volume=95.0,
                  efficiency={'Xe': 1.0, 'Kr': '9.5/mass_flowrate'})


def test_rem_elements():
    mats = serpent.read_dep_comp(iter_inpit_file, True)
    waste = process.rem_elements(mats['fuel'])
    np.testing.assert_almost_equal(waste[541350000], 19.79776930513891)
    np.testing.assert_almost_equal(waste[541360000], 176.44741987005173)
    np.testing.assert_almost_equal(waste[541280000], 9.911913132605642e-05)
    np.testing.assert_almost_equal(waste[541390000], 0.026158507248944377)
    np.testing.assert_almost_equal(waste[360790000], 6.420212330439721e-17)
    np.testing.assert_almost_equal(waste[360800000], 1.6462261463853208e-06)
    np.testing.assert_almost_equal(waste[360920000], 0.0002724894672886946)
    np.testing.assert_almost_equal(waste[360860000], 26.847312879174968)
    assert waste.mass == 531.0633118374121
