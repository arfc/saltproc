"""Test OpenMC file interface"""
import json
from os import remove
from pathlib import Path

import numpy as np
import pytest
import openmc


@pytest.fixture
def geometry_switch(scope='module'):
    path = Path(__file__).parents[2]
    return (path / 'openmc_data' / 'geometry_switch.xml')


def test_write_runtime_input(openmc_depcode, openmc_reactor):
    initial_geometry_file = openmc_depcode.geo_file_paths[0]

    # compare settings, geometry, and material files
    settings_file = openmc_depcode.template_input_file_path['settings']
    geometry_file = openmc_depcode.geo_file_paths[0]
    materials_file = openmc_depcode.template_input_file_path['materials']
    ref_files = (settings_file, geometry_file, materials_file)

    # write_runtime_input
    openmc_depcode.write_runtime_input(openmc_reactor,
                                        0,
                                        False)

    settings_file = openmc_depcode.runtime_inputfile['settings']
    geometry_file = openmc_depcode.runtime_inputfile['geometry']
    material_file = openmc_depcode.runtime_matfile
    test_files = (settings_file, geometry_file, materials_file)

    for ref_file, test_file in zip(ref_files, test_files):
        ref_filelines = openmc_depcode.read_plaintext_file(ref_file)
        test_filelines = openmc_depcode.read_plaintext_file(test_file)
        for i in range(len(ref_filelines)):
            assert ref_filelines[i] == test_filelines[i]

    openmc_depcode.geo_file_paths *= 2
    openmc_depcode.geo_file_paths[0] = initial_geometry_file


def test_update_depletable_materials(openmc_depcode, openmc_reactor):
    initial_geometry_file = openmc_depcode.geo_file_paths[0]
    # write_runtime_input
    openmc_depcode.write_runtime_input(openmc_reactor,
                                        0,
                                        False)
    # update_depletable_materials
    old_output_path = openmc_depcode.output_path

    # switch output_path to where read_depleted_materials will pick up the correct database
    openmc_depcode.output_path = Path(openmc_depcode.runtime_matfile).parents[1]
    ref_materials = openmc_depcode.read_depleted_materials(True)
    openmc_depcode.output_path = old_output_path

    openmc_depcode.update_depletable_materials(ref_materials, 12.0)
    test_mats = openmc.Materials.from_xml(openmc_depcode.runtime_matfile)

    # compare material objects
    for material in test_mats:
        if material.name in ref_mats.keys():
            ref_material = ref_mats[material.name]
            test_material = openmc_depcode._create_mass_percents_dictionary(material)
            for key in test_material.keys():
                np.testing.assert_almost_equal(ref_material[key], test_material[key], decimal=5)

    remove(openmc_depcode.runtime_matfile)
    openmc_depcode.geo_file_paths *= 2
    openmc_depcode.geo_file_paths[0] = initial_geometry_file


def test_write_depletion_settings(openmc_depcode, openmc_reactor):
    """
    Unit test for `Depcodeopenmc_depcode.write_depletion_settings`
    """
    openmc_depcode.write_depletion_settings(openmc_reactor, 0)
    with open(openmc_depcode.output_path / 'depletion_settings.json') as f:
        j = json.load(f)
        assert Path(j['directory']).resolve() == Path(
            openmc_depcode.output_path)
        assert j['timesteps'][0] == openmc_reactor.depletion_timesteps[0]
        assert j['operator_kwargs']['chain_file'] == \
            openmc_depcode.chain_file_path
        assert j['integrator_kwargs']['power'] == openmc_reactor.power_levels[0]
        assert j['integrator_kwargs']['timestep_units'] == 'd'


def test_write_saltproc_openmc_tallies(openmc_depcode):
    """
    Unit test for `OpenMCDepcode.write_saltproc_openmc_tallies`
    """
    mat = openmc.Materials.from_xml(
        openmc_depcode.template_input_file_path['materials'])
    geo = openmc.Geometry.from_xml(
        openmc_depcode.geo_file_paths[0], mat)
    openmc_depcode.write_saltproc_openmc_tallies(mat, geo)
    del mat, geo
    tallies = openmc.Tallies.from_xml(openmc_depcode.runtime_inputfile['tallies'])

    # now write asserts statements based on the openmc_depcode.Tallies API and
    # what we expect our tallies to be
    assert len(tallies) == 7
    tal0 = tallies[0]
    tal1 = tallies[1]
    tal2 = tallies[2]
    tal3 = tallies[3]
    tal4 = tallies[4]
    tal5 = tallies[5]
    tal6 = tallies[6]

    assert isinstace(tal0.filters[0], openmc.UniverseFilter)
    assert isinstace(tal0.filters[1], openmc.DelayedGroupFilter)
    assert tal0.scores[0] == 'delayed-nu-fission'

    assert isinstace(tal1.filters[0], openmc.UniverseFilter)
    assert isinstace(tal1.filters[1], openmc.DelayedGroupFilter)
    assert tal1.scores[0] == 'decay-rate'

    assert isinstace(tal2.filters[0], openmc.UniverseFilter)
    assert isinstace(tal2.filters[1], openmc.EnergyFilter)
    assert tal2.scores[0] == 'nu-fission'

    assert isinstace(tal3.filters[0], openmc.UniverseFilter)
    assert isinstace(tal3.filters[1], openmc.DelayedGroupFilter)
    assert isinstace(tal3.filters[1], openmc.EnergyFilter)
    assert tal3.scores[0] == 'delayed-nu-fission'

    assert tal4.name == 'breeding_ratio_tally'
    assert isinstance(tal4.filters[0], openmc.UniverseFilter)
    assert tal4.scores[0] == '(n,gamma)'
    assert tal4.scores[1] == 'absorption'

    assert tal5.name == 'fission_energy'
    assert isinstance(tal5.filters[0], openmc.UniverseFilter)
    assert tal5.scores[2] == 'kappa-fission'

    assert tal6.name == 'heating'
    assert isinstance(tal6.filters[0], openmc.UniverseFilter)
    assert tal6.scores[0] == 'heating'


def test_switch_to_next_geometry(openmc_depcode, openmc_reactor):
    initial_geometry_file = openmc_depcode.geo_file_paths[0]
    ref_geometry_file = openmc_depcode.geo_file_paths[1]

    # write_runtime_input
    openmc_depcode.write_runtime_input(openmc_reactor,
                                        0,
                                        False)

    openmc_depcode.switch_to_next_geometry()
    test_geometry_file = openmc_depcode.runtime_inputfile['geometry']

    ref_filelines = openmc_depcode.read_plaintext_file(ref_geometry_file)
    test_filelines = openmc_depcode.read_plaintext_file(test_geometry_file)
    for i in range(len(ref_filelines)):
        assert ref_filelines[i] == test_filelines[i]

    openmc_depcode.geo_file_paths = [initial_geometry_file, ref_geometry_file]
