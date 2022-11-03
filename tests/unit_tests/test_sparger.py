"""Test Sparger functions"""
import numpy as np
import pytest

from saltproc import Sparger


@pytest.fixture(scope='module')
def sparger():
    sparger = Sparger(mass_flowrate=10,
                      capacity=99.0,
                      volume=95.0,
                      efficiency="self")
    return sparger


def test_rem_elements(serpent_depcode, sparger):
    mats = serpent_depcode.read_dep_comp(True)
    thru, waste = sparger.process_material(mats['fuel'])
    np.testing.assert_almost_equal(waste[541350000], 8.061014535231715)
    np.testing.assert_almost_equal(waste[541360000], 71.8437109936129)
    np.testing.assert_almost_equal(waste[541280000], 4.0358120454079906e-05)
    np.testing.assert_almost_equal(waste[541390000], 0.010650902326605592)
    np.testing.assert_almost_equal(waste[360790000], 6.420212330439721e-17)
    np.testing.assert_almost_equal(waste[360800000], 7.029023635956131e-07)
    np.testing.assert_almost_equal(waste[360920000], 0.00011634701042301513)
    np.testing.assert_almost_equal(waste[360860000], 11.463212220507412)
    assert waste.mass == 217.43479356542446
