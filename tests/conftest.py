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
    depcode_input, simulation_input, reactor_input = \
        read_main_input(saltproc_input)[-1]
    depcode = _create_depcode_object(depcode_input)
    depcode.runtime_inputfile = str(cwd / 'serpent_data' / 'tap_reference')
    output_dir = str(depcode.output_path).split('/')[-1]
    depcode.output_path = tmpdir_factory.mktemp(f'serpent_{output_dir}')

    simulation = _create_simulation_object(simulation_input, depcode)

    reactor = _create_reactor_object(reactor_input)

    return depcode, simulation, reactor


@pytest.fixture(scope='session')
def serpent_depcode(serpent_runtime):
    """SerpentDepcode object for unit tests"""
    depcode  = serpent_runtime[0]
    return depcode


@pytest.fixture(scope='session')
def serpent_reactor(serpent_runtime):
    reactor = serpent_runtime[2]
    return reactor


@pytest.fixture(scope='session')
def simulation(serpent_runtime):
    """Simulation object for unit tests"""
    simulation = serpent_runtime[1]
    return simulation


@pytest.fixture(scope='session')
def openmc_runtime(cwd, tmpdir_factory):
    """SaltProc objects for OpenMC unit tests"""
    saltproc_input = str(cwd / 'openmc_data' / 'msbr_input.json')
    depcode_input, simulation_input, reactor_input = \
        read_main_input(saltproc_input)[-1]
    output_dir = str(depcode_input['output_path']).split('/')[-1]
    tmp_path = tmpdir_factory.mktemp(f'openmc_{output_dir}')
    depcode_input['output_path'] = Path(tmp_path)
    depcode = _create_depcode_object(depcode_input)
    reactor = _create_reactor_object(reactor_input)

    return depcode, reactor


@pytest.fixture(scope='session')
def openmc_depcode(openmc_runtime):
    """OpenMCDepcode objects for unit tests"""
    depcode = openmc_runtime[0]
    return depcode


@pytest.fixture(scope='session')
def openmc_reactor(openmc_runtime):
    reactor = openmc_runtime[1]
    return reactor
