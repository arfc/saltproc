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

    code_input = codename + '_data'
    out = app.read_main_input(main_input / code_input / 'test.json')
    process_input_file, path_input_file, object_input = out
    depcode_input, simulation_input, reactor_input = object_input

    if codename == 'serpent':
        ext = '.ini'
    elif codename == 'openmc':
        ext = '.xml'

    assert depcode_input['codename'] == codename
    assert depcode_input['npop'] == 50
    assert depcode_input['active_cycles'] == 20
    assert depcode_input['inactive_cycles'] == 20
    ## add generic path
    assert depcode_input['geo_file_paths'][0] == (main_input / code_input / ('geometry_base' + ext))

    ## add generic path
    assert simulation_input['db_name'] == (main_input / 'temp_data/db_saltproc.h5')
    assert simulation_input['restart_flag'] is False

    np.testing.assert_equal(
        reactor_input['power_levels'], [
            1.250E+9, 1.250E+9])
    np.testing.assert_equal(reactor_input['dep_step_length_cumulative'],
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
