"""Test Process functions"""
import numpy as np
import pytest

from saltproc import Process


@pytest.fixture(scope='module')
def process():
    process = Process(mass_flowrate=10,
                      capacity=99.0,
                      volume=95.0,
                      efficiency={'Xe': 1.0, 'Kr': '9.5/mass_flowrate'})
    return process


def test_process_material(serpent_depcode, process):
    mats = serpent_depcode.read_depleted_materials(True)
    thru, waste = process.process_material(mats['fuel'])
    np.testing.assert_almost_equal(waste.get_mass('Xe135'), 19.7977787475)
    np.testing.assert_almost_equal(waste.get_mass('Xe136'), 176.44750402500003)
    np.testing.assert_almost_equal(waste.get_mass('Xe128'), 9.911913132605642e-05)
    np.testing.assert_almost_equal(waste.get_mass('Xe139'), 0.026158507248944377)
    np.testing.assert_almost_equal(waste.get_mass('Kr79'), 6.420212330439721e-17)
    np.testing.assert_almost_equal(waste.get_mass('Kr80'), 1.6462261463853208e-06)
    np.testing.assert_almost_equal(waste.get_mass('Kr92'), 0.0002724894672886946)
    np.testing.assert_almost_equal(waste.get_mass('Kr86'), 26.84732568375)
    assert waste.mass == 531.0635651230967


def test_calculate_removal_efficiency(process):
    for component, efficiency in process.efficiency.items():
        calculated_efficiency = process.calculate_removal_efficiency(component)
        if isinstance(efficiency, float):
            assert calculated_efficiency == efficiency
        elif isinstance(efficiency, str):
            assert calculated_efficiency == 9.5 / process.mass_flowrate
