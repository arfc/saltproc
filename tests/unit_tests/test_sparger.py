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
    mats = serpent_depcode.read_depleted_materials(True)
    thru, waste = sparger.process_material(mats['fuel'])
    np.testing.assert_allclose(waste.get_mass('Xe135'), 8.061014535231715, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Xe136'), 71.8437109936129, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Xe128'), 4.0358120454079906e-05, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Xe139'), 0.010650902326605592, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr79'), 5.208452501967084e-16, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr80'), 7.029023635956131e-07, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr92'), 0.00011634701042301513, rtol=1e-6)
    np.testing.assert_allclose(waste.get_mass('Kr86'), 11.463212220507412, rtol=1e-6)
    np.testing.assert_allclose(waste.mass, 217.43479356542446, rtol=1e-6)
