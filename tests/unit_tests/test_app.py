"""Test methods in the app package"""
from pathlib import Path

import numpy as np
import pytest
from saltproc.app import read_main_input, read_processes_from_input
from saltproc.app import read_feeds_from_input, read_dot

@pytest.mark.parametrize("codename, ext", [
    ("serpent", ".ini"),
    ("openmc", ".xml")])
def test_read_main_input(cwd, codename, ext):
    data_path = codename + '_data'
    data_path = cwd / data_path
    main_input = (data_path / 'test_input.json').as_posix()
    out = read_main_input(main_input)
    input_path, process_input_file, path_input_file, object_input = out
    depcode_input, simulation_input, reactor_input = object_input

    assert input_path == data_path

    assert depcode_input['codename'] == codename
    assert depcode_input['npop'] == 50
    assert depcode_input['active_cycles'] == 20
    assert depcode_input['inactive_cycles'] == 20
    assert depcode_input['geo_file_paths'][0] == \
        (data_path / ('geometry_base' + ext)).as_posix()

    assert simulation_input['db_name'] == \
        (data_path / '../temp_data/db_saltproc.h5').resolve().as_posix()
    assert simulation_input['restart_flag'] is False

    np.testing.assert_equal(
        reactor_input['power_levels'], [
            1.250E+9, 1.250E+9])
    np.testing.assert_equal(reactor_input['dep_step_length_cumulative'],
                            [5, 10])

def test_read_processes_from_input(proc_test_file):
    procs = read_processes_from_input(proc_test_file)
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
    feeds = read_feeds_from_input(proc_test_file)
    assert feeds['fuel']['leu'].mass == 4.9602E+8
    assert feeds['fuel']['leu'].density == 4.9602
    assert feeds['fuel']['leu']['U235'] == 15426147.398592
    assert feeds['fuel']['leu']['U238'] == 293096800.37484

def test_read_dot(path_test_file):
    burnable_mat, paths = read_dot(path_test_file)
    assert burnable_mat == 'fuel'
    assert paths[0][1] == 'sparger'
    assert paths[1][-2] == 'heat_exchanger'
    assert np.shape(paths) == (2, 7)
