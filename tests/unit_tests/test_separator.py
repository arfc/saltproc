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


def test_rem_elements(serpent_depcode, separator):
    mats = serpent_depcode.read_depleted_materials(True)
    thru, waste = separator.process_material(mats['fuel'])
    np.testing.assert_allclose(waste.get_mass('Xe135'), 19.5320018359295, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Xe136'), 174.0787699729534, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Xe128'), 9.778854502227908e-05, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Xe139'), 0.025807352522232645, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr79'), 1.2668053364239955e-15, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr80'), 1.709607392097611e-06, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr92'), 0.0002829805665329617, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr86'), 27.88095952489617, rtol=1e-6)
    np.testing.assert_allclose(waste.mass, 527.0884551454453, rtol=1e-6)
