"""Test methods in the app package"""
from pathlib import Path

import numpy as np
import pytest
from saltproc.app import read_main_input, get_extraction_processes
from saltproc.app import get_feeds, get_extraction_process_paths


@pytest.mark.parametrize("codename, ext", [
    ("serpent", ".ini"),
    ("openmc", ".xml")])
def test_read_main_input(cwd, codename, ext):
    data_path = codename + '_data'
    data_path = cwd / data_path
    main_input = str(data_path / 'tap_input.json')
    out = read_main_input(main_input)
    input_path, process_input_file, path_input_file, object_input = out
    depcode_input, simulation_input, reactor_input = object_input

    assert input_path == data_path

    assert depcode_input['codename'] == codename
    assert depcode_input['geo_file_paths'][0] == \
        str(data_path / ('tap_geometry_base' + ext))
    if codename == 'openmc':
        assert depcode_input['template_input_file_path'] == \
            {'materials': str((input_path / 'tap_materials.xml').resolve()),
             'settings': str((input_path / 'tap_settings.xml').resolve())}
        assert depcode_input['chain_file_path'] == \
            str((input_path / 'test_chain.xml').resolve())
        assert depcode_input['depletion_settings'] == \
            {'method': 'predictor',
             'final_step': True,
             'operator_kwargs': {'normalization_mode': 'fission-q',
                                 'fission_q': None,
                                 'dilute_initial': 1000,
                                 'fission_yield_mode': 'constant',
                                 'reaction_rate_mode': 'direct',
                                 'reaction_rate_opts': None,
                                 'reduce_chain': False,
                                 'reduce_chain_level': None},
             'output': True,
             'integrator_kwargs': {}}
    elif codename == 'serpent':
        assert depcode_input['template_input_file_path'] == \
            str((input_path / 'tap_template.ini').resolve())

    assert simulation_input['db_name'] == \
        str((data_path / f'../{codename}_data/saltproc_runtime/saltproc_results.h5').resolve())
    assert simulation_input['restart_flag'] is False

    np.testing.assert_equal(
        reactor_input['power_levels'], [
            1.250E+9, 1.250E+9])
    np.testing.assert_equal(reactor_input['depletion_timesteps'],
                            [5, 5])

    assert reactor_input['timestep_units'] == 'd'
    assert reactor_input['timestep_type'] == 'stepwise'

def test_get_extraction_processes(proc_test_file):
    procs = get_extraction_processes(proc_test_file)
    assert procs['fuel']['heat_exchanger'].volume == 1.37E+7
    assert procs['fuel']['sparger'].efficiency['H'] == 0.6
    assert procs['fuel']['sparger'].efficiency['Kr'] == 0.6
    assert procs['fuel']['sparger'].efficiency['Xe'] == 0.6
    assert procs['fuel']['entrainment_separator'].efficiency['H'] == 0.15
    assert procs['fuel']['entrainment_separator'].efficiency['Kr'] == 0.87
    assert procs['ctrlPois']['removal_tb_dy'].volume == 11.0
    assert procs['ctrlPois']['removal_tb_dy'].efficiency['Tb'] == 0
    assert procs['ctrlPois']['removal_tb_dy'].efficiency['Dy'] == 0


def test_get_feeds(proc_test_file):
    feeds = get_feeds(proc_test_file)
    assert feeds['fuel']['leu'].mass == 4.9602E+8
    assert feeds['fuel']['leu'].density == 4.9602
    assert feeds['fuel']['leu']['U235'] == 15426147.398592
    assert feeds['fuel']['leu']['U238'] == 293096800.37484


def test_get_extraction_process_paths(path_test_file):
    burnable_mat, paths = get_extraction_process_paths(path_test_file)
    assert burnable_mat == 'fuel'
    assert paths[0][1] == 'sparger'
    assert paths[1][-2] == 'heat_exchanger'
    assert np.shape(paths) == (2, 7)
