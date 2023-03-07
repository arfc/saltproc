"""Test Serpent file interface"""
from os import remove
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def geometry_switch(scope='module'):
    path = Path(__file__).parents[2]
    return (path / 'serpent_data' / 'tap_geometry_switch.ini')


def test_runtime_input_from_template(serpent_depcode, serpent_reactor):
    file = serpent_depcode.template_input_file_path
    file_data = serpent_depcode.read_plaintext_file(file)

    serpent_depcode.get_neutron_settings(file_data)

    # insert_path_to_geometry
    file_data = serpent_depcode.insert_path_to_geometry(file_data)
    assert file_data[5].split('/')[-1] == 'tap_geometry_base.ini"\n'

    # create_runtime_matfile
    file_data = serpent_depcode.create_runtime_matfile(file_data)
    assert file_data[0].split()[-1] == '\"' + \
        serpent_depcode.runtime_matfile + '\"'

    # get_burnable_material_card_data
    burnable_material_card_data = {'fuel':
                                  (['mat',
                                    'fuel',
                                    '-4.960200000E+00',
                                    'rgb',
                                    '253',
                                    '231',
                                    '37',
                                    'burn',
                                    '1',
                                    'fix',
                                    '09c',
                                    '900',
                                    'vol',
                                    '4.435305E+7',
                                    '%',
                                    'just',
                                    'core',
                                    'volume',
                                    '2.27175E+07'], 13),
                                  'ctrlPois':
                                  (['mat',
                                    'ctrlPois',
                                    '-2.52',
                                    'burn',
                                    '1',
                                    'fix',
                                    '09c',
                                    '900',
                                    'rgb',
                                    '255',
                                    '128',
                                    '0',
                                    'vol',
                                    '1.11635E+04'], 13)}

    for ref_key, test_key in \
    zip(serpent_depcode._burnable_material_card_data.keys(),
     burnable_material_card_data.keys()):
        assert ref_key == test_key
        ref_data = serpent_depcode._burnable_material_card_data[ref_key]
        test_data = burnable_material_card_data[test_key]
        np.testing.assert_array_equal(np.array(ref_data, dtype=object),
                                      np.array(test_data, dtype=object))

    remove(serpent_depcode.runtime_matfile)

    # set_power_load
    for idx in range(len(serpent_reactor.power_levels)):
        file_data = serpent_depcode.set_power_load(file_data, serpent_reactor, idx)

        assert file_data[8].split()[4] == 'daystep'
        assert file_data[8].split()[2] == str("%5.9E" % serpent_reactor.power_levels[idx])
        assert file_data[8].split()[5] == str("%7.5E" % serpent_reactor.depletion_timesteps[idx])


def test_write_runtime_files(serpent_depcode, serpent_reactor):
    mats = serpent_depcode.read_depleted_materials(True)

    # update_depletable_materials
    serpent_depcode.update_depletable_materials(mats, 12.0)
    file = serpent_depcode.runtime_matfile
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
    remove(serpent_depcode.runtime_matfile)

    # write_runtime_input
    serpent_depcode.write_runtime_input(serpent_reactor,
                                        0,
                                        False)

    file = serpent_depcode.runtime_inputfile
    file_data = serpent_depcode.read_plaintext_file(file)
    assert file_data[0] == f'include "{serpent_depcode.runtime_matfile}"\n'
    assert file_data[8].split()[2] == '1.250000000E+09'
    assert file_data[8].split()[4] == 'daystep'
    assert file_data[8].split()[-1] == '5.00000E+00'
    assert file_data[20] == 'set pop 50 20 20\n'

    # switch_to_next_geometry
    serpent_depcode.geo_file_paths += ['../../examples/406.inp',
                                  '../../examples/988.inp']
    serpent_depcode.switch_to_next_geometry()
    file_data = serpent_depcode.read_plaintext_file(file)
    assert file_data[5].split('/')[-1] == '406.inp"\n'

    remove(serpent_depcode.runtime_inputfile)
