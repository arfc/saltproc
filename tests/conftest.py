from pathlib import Path
import pytest

from saltproc.app import read_main_input, _create_depcode_object, _create_simulation_object, _create_reactor_object
from saltproc import Simulation


@pytest.fixture(scope='session')
def cwd():
    return Path(__file__).parents[0]


@pytest.fixture(scope='session')
def proc_test_file(cwd):
    filename = (cwd / 'tap_processes.json')
    return filename


@pytest.fixture(scope='session')
def path_test_file(cwd):
    filename = (cwd / 'tap_paths.dot')
    return filename


@pytest.fixture(scope='session')
def serpent_runtime(cwd, tmpdir_factory):
    """SaltProc objects for Serpent unit tests"""
    saltproc_input = str(cwd / 'serpent_data' / 'tap_input.json')
    _, _, _, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])
    depcode.runtime_inputfile = str(cwd / 'serpent_data' / 'tap_reference')
    output_dir = str(depcode.output_path).split('/')[-1]
    depcode.output_path = tmpdir_factory.mktemp(f'serpent_{output_dir}')

    simulation = _create_simulation_object(object_input[1], depcode, 1, 1)
        #db_path=str(
        #    cwd /
        #    'serpent_data' /
        #    'tap_reference_db.h5'))

    reactor = _create_reactor_object(object_input[2])

    return depcode, simulation, reactor


@pytest.fixture(scope='session')
def serpent_depcode(serpent_runtime):
    """SerpentDepcode object for unit tests"""
    depcode, _, _ = serpent_runtime
    return depcode


@pytest.fixture(scope='session')
def serpent_reactor(serpent_runtime):
    _, _, reactor = serpent_runtime
    return reactor


@pytest.fixture(scope='session')
def simulation(serpent_runtime):
    """Simulation object for unit tests"""
    _, simulation, _ = serpent_runtime
    return simulation


@pytest.fixture(scope='session')
def openmc_runtime(cwd, tmpdir_factory):
    """SaltProc objects for OpenMC unit tests"""
    saltproc_input = str(cwd / 'openmc_data' / 'tap_input.json')
    _, _, _, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])
    output_dir = str(depcode.output_path).split('/')[-1]
    depcode.output_path = tmpdir_factory.mktemp(f'openmc_{output_dir}')
    reactor = _create_reactor_object(object_input[2])

    return depcode, reactor


@pytest.fixture(scope='session')
def openmc_depcode(openmc_runtime):
    """OpenMCDepcode objects for unit tests"""
    depcode, _ = openmc_runtime
    return depcode


@pytest.fixture(scope='session')
def openmc_reactor(openmc_runtime):
    _, reactor = openmc_runtime
    return reactor
