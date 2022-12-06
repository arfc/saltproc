from pathlib import Path
import pytest

from saltproc.app import read_main_input, _create_depcode_object
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
def serpent_depcode(cwd):
    """SerpentDepcode object for unit tests"""
    saltproc_input = str(cwd / 'serpent_data' / 'tap_input.json')
    _, _, _, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])
    depcode.runtime_inputfile = str(cwd / 'serpent_data' / 'tap_reference')

    return depcode


@pytest.fixture(scope='session')
def openmc_depcode(cwd):
    """OpenMCDepcode object for unit tests"""
    saltproc_input = str(cwd / 'openmc_data' / 'tap_input.json')
    _, _, _, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])

    return depcode


@pytest.fixture(scope='session')
def simulation(cwd, serpent_depcode):
    """Simulation object for unit tests"""
    simulation = Simulation(
        sim_name='test_simulation',
        sim_depcode=serpent_depcode,
        core_number=1,
        node_number=1,
        db_path=str(
            cwd /
            'serpent_data' /
            'tap_reference_db.h5'))
    return simulation
