"""Test Serpent file interface"""
from os import remove
from pathlib import Path

import numpy as np
import pytest

from saltproc import Reactor


@pytest.fixture
def geometry_switch(scope='module'):
    path = Path(__file__).parents[2]
    return (path / 'serpent_data' / 'tap_geometry_switch.ini')


@pytest.fixture
def msr(scope='module'):
    reactor = Reactor(volume=1.0,
                      power_levels=[1.250E+09, 1.250E+09, 5.550E+09],
                      dep_step_length_cumulative=[111.111, 2101.9, 3987.5])
    return reactor


def test_iter_input_from_template(serpent_depcode, msr):
    file = serpent_depcode.template_input_file_path
    file_data = serpent_depcode.read_plaintext_file(file)

    # change_sim_par
    file_data = serpent_depcode.apply_neutron_settings(file_data)
    assert file_data[18] == 'set pop %i %i %i\n' % (
        serpent_depcode.npop,
        serpent_depcode.active_cycles,
        serpent_depcode.inactive_cycles)

    # insert_path_to_geometry
    file_data = serpent_depcode.insert_path_to_geometry(file_data)
    assert file_data[5].split('/')[-1] == 'tap_geometry_base.ini"\n'

    # create_runtime_matfile
    file_data = serpent_depcode.create_runtime_matfile(file_data)
    assert file_data[0].split()[-1] == '\"' + \
        serpent_depcode.iter_matfile + '\"'
    remove(serpent_depcode.iter_matfile)

    # replace_burnup_parameters
    time = msr.dep_step_length_cumulative.copy()
    time.insert(0, 0.0)
    depsteps = np.diff(time)
    for idx in range(len(msr.power_levels)):
        file_data = serpent_depcode.replace_burnup_parameters(file_data,
                                                              msr,
                                                              idx)

        assert file_data[8].split()[4] == 'daystep'
        assert file_data[8].split()[2] == str("%5.9E" % msr.power_levels[idx])
        assert file_data[8].split()[5] == str("%7.5E" % depsteps[idx])


def test_write_iter_files(serpent_depcode, msr):
    mats = serpent_depcode.read_depleted_materials(True)

    # update_depletable_materials
    serpent_depcode.update_depletable_materials(mats, 12.0)
    file = serpent_depcode.iter_matfile
    file_data = serpent_depcode.read_plaintext_file(file)
    assert file_data[0] == '% Material compositions (after 12.000000 days)\n'
    if 'fuel' in file_data[3]:
        assert file_data[3].split()[-1] == '2.27175E+07'
        assert file_data[3].split()[2] == '-4.960200000E+00'
        assert file_data[1663].split()[-1] == '1.11635E+04'
        assert file_data[1664] == \
            '            1001.09c  -1.21000137902945E-35\n'
    elif 'ctrlPois' in file_data[3]:
        assert file_data[3].split()[-1] == '1.11635E+04'
        assert file_data[4] == '            1001.09c  -1.21000137902945E-35\n'
    remove(serpent_depcode.iter_matfile)

    # write_depcode_input
    serpent_depcode.write_depcode_input(msr,
                                        0,
                                        False)

    file = serpent_depcode.iter_inputfile
    file_data = serpent_depcode.read_plaintext_file(file)
    assert file_data[0] == 'include "./serpent_iter_mat.ini"\n'
    assert file_data[8].split()[2] == '1.250000000E+09'
    assert file_data[8].split()[4] == 'daystep'
    assert file_data[8].split()[-1] == '1.11111E+02'
    assert file_data[20] == 'set pop 50 20 20\n'

    # switch_to_next_geometry
    serpent_depcode.geo_files += ['../../examples/406.inp',
                                  '../../examples/988.inp']
    serpent_depcode.switch_to_next_geometry()
    file_data = serpent_depcode.read_plaintext_file(file)
    assert file_data[5].split('/')[-1] == '406.inp"\n'

    remove(serpent_depcode.iter_inputfile)
