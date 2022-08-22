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


def test_rem_elements(depcode_serpent, process):
    mats = depcode_serpent.read_dep_comp(True)
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


def test_calculate_rem_efficiency(process):
    for component, efficiency in process.efficiency.items():
        calculated_efficiency = process.calc_rem_efficiency(component)
        if isinstance(efficiency, float):
            assert calculated_efficiency == efficiency
        elif isinstance(efficiency, str):
            assert calculated_efficiency == 9.5 / process.mass_flowrate

