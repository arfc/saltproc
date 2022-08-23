from pathlib import Path
import pytest

from saltproc.app import read_main_input, _create_depcode_object

@pytest.fixture
def cwd(scope='module'):
    return Path(__file__).parents[0]

@pytest.fixture
def proc_test_file(cwd, scope='session'):
    filename = (cwd / 'test_processes.json')
    return filename


@pytest.fixture
def path_test_file(cwd, scope='session'):
    filename = (cwd / 'test_paths.dot')
    return filename


@pytest.fixture
def depcode_serpent(cwd, scope='session'):
    saltproc_input = (cwd / 'serpent_data' / 'test_input.json').as_posix()
    _, _, _, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])
    depcode.iter_inputfile = (cwd / 'serpent_data' / 'ref').as_posix()

    return depcode

@pytest.fixture
def depcode_openmc(cwd, scope='session'):
    saltproc_input = (cwd / 'openmc_data' / 'test_input.json').as_posix()
    _, _, _, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])

    # Openmc initlialization
    openmc_input_path = (cwd / 'openmc_data')

    openmc_iter_inputfiles = {
        "geometry": "geometry.xml",
        "settings": "settings.xml",
    }

    for key in openmc_iter_inputfiles:
        openmc_iter_inputfiles[key] = \
            (openmc_input_path / openmc_iter_inputfiles[key]).as_posix()

    depcode.iter_inputfile = openmc_iter_inputfiles
    depcode.iter_matfile = (openmc_input_path / 'materials.xml').as_posix()

    return depcode
