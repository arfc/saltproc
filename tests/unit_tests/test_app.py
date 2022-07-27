"""Test methods in the app package"""

from pathlib import Path

import numpy as np
import pytest
from saltproc import app


@pytest.fixture
def main_input():
    path = Path(__file__).parents[1]
    filename = path
    return filename

@pytest.fixture
def proc_test_file():
    path = Path(__file__).parents[1]
    filename = (path / 'test_processes.json')
    return filename

@pytest.fixture
def dot_test_file():
    path = Path(__file__).parents[1]
    filename = (path / 'test.dot')
    return filename

@pytest.mark.parametrize("codename", ("serpent", "openmc"))
def test_read_main_input(main_input, codename):
    app.read_main_input((main_input / codename + '_data' / 'test.json'))
    assert app.depcode_inp['codename'] == codename
    assert app.depcode_inp['npop'] == 50
    assert app.depcode_inp['active_cycles'] == 20
    assert app.depcode_inp['inactive_cycles'] == 20
    ## add generic path
    assert app.simulation_inp['db_name'] == ... 'db_saltproc.h5'
    ## add generic path
    assert app.depcode_inp['geo_file_paths'] == ...
    assert app.simulation_inp['restart_flag'] is False
    np.testing.assert_equal(
        app.reactor_inp['power_levels'], [
            1.250E+9, 1.250E+9])
    np.testing.assert_equal(app.reactor_inp['dep_step_length_cumulative'],
                            [5, 10])

def test_read_processes_from_input(proc_test_file):
    procs = app.read_processes_from_input(proc_test_file)
    assert procs['fuel']['heat_exchanger'].volume == 1.37E+7
    assert procs['fuel']['sparger'].efficiency['H'] == 0.6
    assert procs['fuel']['sparger'].efficiency['Kr'] == 0.6
    assert procs['fuel']['sparger'].efficiency['Xe'] == 0.6
    assert procs['fuel']['entrainment_separator'].efficiency['H'] == 0.15
    assert procs['fuel']['entrainment_separator'].efficiency['Kr'] == 0.87
    assert procs['ctrlPois']['removal_tb_dy'].volume == 11.0
    assert procs['ctrlPois']['removal_tb_dy'].efficiency['Tb'] == 0
    assert procs['ctrlPois']['removal_tb_dy'].efficiency['Dy'] == 0

def test_read_feeds_from_input(proc_test_file):
    feeds = app.read_feeds_from_input(proc_test_file)
    assert feeds['fuel']['leu'].mass == 4.9602E+8
    assert feeds['fuel']['leu'].density == 4.9602
    assert feeds['fuel']['leu']['U235'] == 15426147.398592
    assert feeds['fuel']['leu']['U238'] == 293096800.37484


def test_read_dot(dot_test_file):
    burnable_mat, paths = app.read_dot(dot_test_file)
    assert burnable_mat == 'fuel'
    assert paths[0][1] == 'sparger'
    assert paths[1][-2] == 'heat_exchanger'
    assert np.shape(paths) == (2, 7)
