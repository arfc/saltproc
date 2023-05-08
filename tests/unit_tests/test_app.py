"""Test methods in the app package"""
from pathlib import Path
import json

import numpy as np
import pytest
from saltproc.app import read_main_input, get_extraction_processes
from saltproc.app import (_validate_depletion_timesteps_power_levels,
                          _convert_cumulative_to_stepwise,
                          _scale_depletion_timesteps)
from saltproc.app import (SECOND_UNITS, MINUTE_UNITS, HOUR_UNITS, DAY_UNITS,
                          YEAR_UNITS)
from saltproc.app import get_feeds, get_extraction_process_paths


@pytest.fixture
def expected_depletion_settings(scope='module'):
    with open(Path(__file__).parents[1] / 'openmc_data/depletion_settings.json') as f:
        expected_depletion_settings = json.load(f)
        #expected_depletion_settings['chain_file'] = \
        #    Path(__file__).parents[1] / 'openmc_data' / expected_depletion_settings['chain_file']
        expected_depletion_settings['operator_kwargs']['fission_q'] = \
            str(Path(__file__).parents[1] / 'openmc_data' / expected_depletion_settings['operator_kwargs']['fission_q'])

        expected_depletion_settings['operator_kwargs'].pop('chain_file')
        expected_depletion_settings['integrator_kwargs'] = {}
        expected_depletion_settings.pop('directory')
        expected_depletion_settings.pop('timesteps')
    return expected_depletion_settings


@pytest.mark.parametrize("codename, ext, reactor_name", [
    ("serpent", ".ini", "tap"),
    ("openmc", ".xml", "msbr")])
def test_read_main_input(cwd, expected_depletion_settings, codename, ext, reactor_name):
    data_path = codename + '_data'
    data_path = cwd / data_path
    main_input = str(data_path / f'{reactor_name}_input.json')
    out = read_main_input(main_input)
    input_path, process_input_file, path_input_file, mpi_args, object_input = out
    depcode_input, simulation_input, reactor_input = object_input

    assert input_path == data_path

    assert mpi_args is None

    assert depcode_input['codename'] == codename
    assert depcode_input['geo_file_paths'][0] == \
        str(data_path / (f'{reactor_name}_geometry_base' + ext))
    assert depcode_input['output_path'] == cwd / (f'{codename}_data/saltproc_runtime')
    if codename == 'openmc':
        assert depcode_input['template_input_file_path'] == \
            {'materials': str((input_path / 'materials.xml').resolve()),
             'settings': str((input_path / f'{reactor_name}_settings.xml').resolve())}
        assert depcode_input['chain_file_path'] == \
            str((input_path / 'chain_endfb71_pwr.xml').resolve())
        assert depcode_input['depletion_settings'] == \
            expected_depletion_settings
        np.testing.assert_equal(reactor_input['power_levels'],
                                [2.250E+9, 2.250E+9])
        np.testing.assert_equal(reactor_input['depletion_timesteps'],
                                [3, 3])

    elif codename == 'serpent':
        assert depcode_input['template_input_file_path'] == \
            str((input_path / f'{reactor_name}_template.ini').resolve())
        assert depcode_input['zaid_convention'] == 'serpent'
        np.testing.assert_equal(reactor_input['power_levels'],
                                [1.250E+9, 1.250E+9])
        np.testing.assert_equal(reactor_input['depletion_timesteps'],
                                [5, 5])

    assert simulation_input['db_name'] == \
        str((data_path / f'../{codename}_data/saltproc_runtime/saltproc_results.h5').resolve())
    assert simulation_input['restart_flag'] is False

    assert reactor_input['timestep_units'] == 'd'
    assert reactor_input['timestep_type'] == 'stepwise'


def test_convert_cumulative_to_stepwise():
    timesteps = _convert_cumulative_to_stepwise([2, 4, 6])
    np.testing.assert_equal(timesteps, [2, 2, 2])


@pytest.mark.parametrize("n_depletion_steps, depletion_timesteps, power_levels, throws_error", [
    (3, [1], [1], False),
    (3, [1], [1, 1, 1], False),
    (3, [1, 1, 1], [1], False),
    (3, [1], [1, 1], True),
    (3, [1, 1], [1, 1], False),
    (None, [1, 1, 1], [1, 1, 1], False),
    (None, [1], [1, 1, 1], True),
    (None, [1, 1, 1], [1], True)])
def test_validate_depletion_timesteps_power_levels(n_depletion_steps,
                                                   depletion_timesteps,
                                                   power_levels,
                                                   throws_error):
    if throws_error:
        with pytest.raises(ValueError):
            _validate_depletion_timesteps_power_levels(n_depletion_steps,
                                                       depletion_timesteps,
                                                       power_levels)
    else:
        depletion_steps, power_levels = \
            _validate_depletion_timesteps_power_levels(n_depletion_steps,
                                                       depletion_timesteps,
                                                       power_levels)
        assert (len(depletion_steps) == 2 or len(depletion_steps) == 3)


@pytest.mark.parametrize("expected_depletion_timesteps, timestep_units", [
    ([1/86400], SECOND_UNITS),
    ([1/1440], MINUTE_UNITS),
    ([1/24], HOUR_UNITS),
    ([1.], DAY_UNITS),
    ([365.25], YEAR_UNITS)
])
def test_scale_depletion_timesteps(expected_depletion_settings,
                                   expected_depletion_timesteps,
                                   timestep_units):
    expected_depletion_timesteps = np.array(expected_depletion_timesteps)
    base_timestep = np.array([1.])
    for unit in timestep_units:
        input_timestep = base_timestep.copy()
        scaled_timesteps = \
            _scale_depletion_timesteps(unit, input_timestep, 'serpent')
        np.testing.assert_equal(scaled_timesteps, expected_depletion_timesteps)
        input_timestep = base_timestep.copy()
        scaled_timesteps = \
            _scale_depletion_timesteps(unit, input_timestep, 'openmc')
        np.testing.assert_equal(scaled_timesteps, base_timestep)
    input_timestep = base_timestep.copy()
    scaled_timesteps = \
        _scale_depletion_timesteps('MWD/KG', input_timestep, 'serpent')
    np.testing.assert_equal(scaled_timesteps, base_timestep)
    input_timestep = base_timestep.copy()
    scaled_timesteps = \
        _scale_depletion_timesteps('MWD/KG', input_timestep, 'openmc')
    np.testing.assert_equal(scaled_timesteps, base_timestep)

    bad_unit = 'months'
    with pytest.raises(IOError,
                       match=f'Unrecognized time unit: {bad_unit}'):
        _scale_depletion_timesteps(bad_unit, [1], 'serpent')


@pytest.mark.parametrize("filename", [
    "constant_fission_yield",
    "cutoff_fission_yield",
    "flux_reaction_rate"])
def test_openmc_depletion_settings(cwd, expected_depletion_settings, filename):
    data_path = 'openmc_data'
    data_path = cwd / data_path
    main_input = str(data_path / f'{filename}_input.json')
    out = read_main_input(main_input)
    input_path, process_input_file, path_input_file, mpi_args, object_input = out
    depcode_input, simulation_input, reactor_input = object_input

    assert depcode_input['template_input_file_path'] == \
        {'materials': str((input_path / 'msbr_materials.xml').resolve()),
         'settings': str((input_path / 'msbr_settings.xml').resolve())}
    assert depcode_input['chain_file_path'] == \
        str((input_path / 'chain_endfb71_pwr.xml').resolve())

    modified_operator_kwargs = expected_depletion_settings['operator_kwargs'].copy()
    if filename == 'constant_fission_yield':

        operator_kwargs = {'fission_yield_opts': {'energy': 0.0253}}
        modified_operator_kwargs.update(operator_kwargs)
    elif filename == 'cutoff_fission_yield':
        operator_kwargs = {'fission_yield_mode': 'cutoff',
                           'fission_yield_opts': {'cutoff': 112.0,
                                                  'thermal_energy': 0.0253,
                                                  'fast_energy': 5.0e5}}
        modified_operator_kwargs.update(operator_kwargs)

    elif filename == 'flux_reaction_rate':
        operator_kwargs = {'reaction_rate_mode': 'flux',
                           'reaction_rate_opts': {'energies': [0.0253, 500000.0],
                                                  'reactions': ['(n,gamma)'],
                                                  'nuclides': ['U235', 'Pu239']}
                           }
        modified_operator_kwargs.update(operator_kwargs)

    assert depcode_input['depletion_settings']['operator_kwargs'] == \
            modified_operator_kwargs


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
    np.testing.assert_almost_equal(feeds['fuel']['leu'].mass, 4.9602E+8)
    np.testing.assert_almost_equal(feeds['fuel']['leu'].density,4.9602)
    np.testing.assert_almost_equal(feeds['fuel']['leu'].comp['U235'] * feeds['fuel']['leu'].mass,
                                   15426147.398592)
    np.testing.assert_almost_equal(feeds['fuel']['leu'].comp['U238'] * feeds['fuel']['leu'].mass,
                                   293096800.37484)


def test_get_extraction_process_paths(path_test_file):
    burnable_mat, paths = get_extraction_process_paths(path_test_file)
    assert burnable_mat == 'fuel'
    assert paths[0][1] == 'sparger'
    assert paths[1][-2] == 'heat_exchanger'
    assert np.shape(paths) == (2, 7)
