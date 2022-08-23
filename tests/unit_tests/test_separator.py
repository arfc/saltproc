"""Test Separator functions"""
import numpy as np
import pytest

from saltproc import Separator

@pytest.fixture(scope='module')
def separator():
    separator = Separator(mass_flowrate=10,
                      capacity=99.0,
                      volume=95.0,
                      efficiency='self')
    return separator


def test_rem_elements(depcode_serpent, separator):
    mats = depcode_serpent.read_dep_comp(True)
    thru, waste = separator.process_material(mats['fuel'])
    np.testing.assert_almost_equal(waste[541350000], 19.5320018359295)
    np.testing.assert_almost_equal(waste[541360000], 174.0787699729534)
    np.testing.assert_almost_equal(waste[541280000], 9.778854502227908e-05)
    np.testing.assert_almost_equal(waste[541390000], 0.025807352522232645)
    np.testing.assert_almost_equal(waste[360790000], 1.2668053364239955e-15)
    np.testing.assert_almost_equal(waste[360800000], 1.709607392097611e-06)
    np.testing.assert_almost_equal(waste[360920000], 0.0002829805665329617)
    np.testing.assert_almost_equal(waste[360860000], 27.88095952489617)
    assert waste.mass == 527.0884551454453
