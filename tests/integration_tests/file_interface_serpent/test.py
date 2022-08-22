"""Test Serpent file interface"""
from os import remove
from pathlib import Path

import numpy as np
import pytest

from saltproc import Reactor

@pytest.fixture
def geometry_switch(scope='module'):
    path = Path(__file__).parents[2]
    return (path / 'serpent_data' / 'geometry_switch.ini')


@pytest.fixture
def msr(scope='module'):
    reactor = Reactor(volume=1.0,
                      power_levels=[1.250E+09, 1.250E+09, 5.550E+09],
                      dep_step_length_cumulative=[111.111, 2101.9, 3987.5])
    return reactor


def test_iter_input_from_template(depcode_serpent, msr):
    file = depcode_serpent.template_input_file_path
    file_data = depcode_serpent.read_plaintext_file(file)

    # change_sim_par
    file_data = depcode_serpent.change_sim_par(file_data)
    assert file_data[18] == 'set pop %i %i %i\n' % (
        depcode_serpent.npop,
        depcode_serpent.active_cycles,
        depcode_serpent.inactive_cycles)

    # insert_path_to_geometry
    file_data = depcode_serpent.insert_path_to_geometry(file_data)
    assert file_data[5].split('/')[-1] == 'geometry_base.ini"\n'

    # create_iter_matfile
    file_data = depcode_serpent.create_iter_matfile(file_data)
    assert file_data[0].split()[-1] == '\"' + depcode_serpent.iter_matfile + '\"'
    remove(depcode_serpent.iter_matfile)

    # replace_burnup_parameters
    time = msr.dep_step_length_cumulative.copy()
    time.insert(0, 0.0)
    depsteps = np.diff(time)
    for idx in range(len(msr.power_levels)):
        file_data = depcode_serpent.replace_burnup_parameters(file_data,
                                                              msr,
                                                              idx)

        assert file_data[8].split()[4] == 'daystep'
        assert file_data[8].split()[2] == str("%5.9E" % msr.power_levels[idx])
        assert file_data[8].split()[5] == str("%7.5E" % depsteps[idx])


def test_write_iter_files(depcode_serpent, msr):
    mats = depcode_serpent.read_dep_comp(True)

    # write_mat_file
    depcode_serpent.write_mat_file(mats, 12.0)
    file = depcode_serpent.iter_matfile
    file_data = depcode_serpent.read_plaintext_file(file)
    assert file_data[0] == '% Material compositions (after 12.000000 days)\n'
    if 'fuel' in file_data[3]:
        assert file_data[3].split()[-1] == '2.27175E+07'
        assert file_data[3].split()[2] == '-4.960200000E+00'
        assert file_data[1663].split()[-1] == '1.11635E+04'
        assert file_data[1664] == '            1001.09c  -1.21000137902945E-35\n'
    elif 'ctrlPois' in file_data[3]:
        assert file_data[3].split()[-1] == '1.11635E+04'
        assert file_data[4] == '            1001.09c  -1.21000137902945E-35\n'
    remove(depcode_serpent.iter_matfile)

    # write_depcode_input
    depcode_serpent.write_depcode_input(msr,
                                0,
                                False)

    file = depcode_serpent.iter_inputfile
    file_data = depcode_serpent.read_plaintext_file(file)
    assert file_data[0] == 'include "./serpent_iter_mat.ini"\n'
    assert file_data[8].split()[2] == '1.250000000E+09'
    assert file_data[8].split()[4] == 'daystep'
    assert file_data[8].split()[-1] == '1.11111E+02'
    assert file_data[20] == 'set pop 50 20 20\n'

    # switch_to_next_geometry
    depcode_serpent.geo_files += ['../../examples/406.inp', '../../examples/988.inp']
    depcode_serpent.switch_to_next_geometry()
    file_data = depcode_serpent.read_plaintext_file(file)
    assert file_data[5].split('/')[-1] == '406.inp"\n'

    remove(depcode_serpent.iter_inputfile)
