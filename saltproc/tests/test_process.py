from __future__ import absolute_import, division, print_function
from saltproc import Process
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
                  output_fname='NONE',
                  iter_matfile=directory+'/material')

process = Process(mass_flowrate=10,
                  capacity=100.0,
                  volume=1.0,
                  # inflow=None,
                  efficiency={'Xe': 1., 'Kr': 0.95})


def test_element_removal():
    mats = serpent.read_dep_comp(input_file, 1)
    # print(mats['fuel'])
    outflow, waste = process.rem_elements(mats['fuel'])
    assert outflow[541350000] == 0.0
    assert outflow[541260000] == 0.0
    assert outflow[541280000] == 0.0
    assert outflow[541470000] == 0.0
    np.testing.assert_almost_equal(outflow[360790000], 6.420212330439721e-17)
    np.testing.assert_almost_equal(outflow[360800000], 8.664348138870117e-08)
    np.testing.assert_almost_equal(outflow[360920000], 1.4341550909931305e-05)
    np.testing.assert_almost_equal(outflow[360860000], 1.4130164673249996)
    assert waste.mass == 531.0633118374121
