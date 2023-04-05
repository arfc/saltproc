"""Test OpenMC file interface"""
import json
import os
from pathlib import Path

import saltproc
import numpy as np
import pytest
import openmc

from saltproc.openmc_depcode import _DELAYED_ENERGY_BOUNDS, _N_DELAYED_GROUPS



@pytest.fixture
def setup(scope='module'):
    os.chdir(Path(__file__).parents[2] / 'openmc_data')

@pytest.fixture
def geometry_switch(scope='module'):
    path = Path(__file__).parents[2]
    return (path / 'openmc_data' / 'geometry_switch.xml')


def test_write_runtime_input(setup, openmc_depcode, openmc_reactor):
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


def test_update_depletable_materials(setup, openmc_depcode, openmc_reactor):
    initial_geometry_file = openmc_depcode.geo_file_paths[0]
    # write_runtime_input
    openmc_depcode.write_runtime_input(openmc_reactor,
                                        0,
                                        False)
    # update_depletable_materials
    old_output_path = openmc_depcode.output_path

    # switch output_path to where read_depleted_materials will pick up the correct database
    openmc_depcode.output_path = Path(__file__).parents[2] / 'openmc_data/saltproc_runtime_ref'

    # Create dummy matfile to read depletion results
    ref_mats = openmc_depcode.read_depleted_materials(True)
    openmc_depcode.output_path = old_output_path

    openmc_depcode.update_depletable_materials(ref_mats, 12.0)
    test_mats = openmc.Materials.from_xml(openmc_depcode.runtime_matfile)

    # compare material objects
    for material in test_mats:
        if material.name in ref_mats.keys():
            ref_material = ref_mats[material.name]
            comp = openmc_depcode._create_mass_percents_dictionary(material, percent_type='wo')
            test_material = saltproc.Materialflow(comp=comp,
                                                  density=material.get_mass_density(),
                                                  volume=material.volume)
            #test_material.set_density('g/cm3', material.get_mass_density())
            #test_material.mass = material.density * material.volume
            #test_material.volume = material.volume
            for key in test_material.comp.keys():
                np.testing.assert_almost_equal(ref_material.comp[key], test_material.comp[key])

    os.remove(openmc_depcode.runtime_matfile)
    # add the initial geometry file back in
    openmc_depcode.geo_file_paths *= 2
    openmc_depcode.geo_file_paths[0] = initial_geometry_file


def test_write_depletion_settings(setup, openmc_depcode, openmc_reactor):
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


def test_write_saltproc_openmc_tallies(setup, openmc_depcode):
    """
    Unit test for `OpenMCDepcode.write_saltproc_openmc_tallies`
    """
    mat = openmc.Materials.from_xml(
        openmc_depcode.template_input_file_path['materials'])
    geo = openmc.Geometry.from_xml(
        openmc_depcode.geo_file_paths[0], mat)
    openmc_depcode.write_saltproc_openmc_tallies(mat, geo,
                                                 _DELAYED_ENERGY_BOUNDS, _N_DELAYED_GROUPS)
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

    assert isinstance(tal0.filters[0], openmc.UniverseFilter)
    assert isinstance(tal0.filters[1], openmc.DelayedGroupFilter)
    assert tal0.scores[0] == 'delayed-nu-fission'

    assert isinstance(tal1.filters[0], openmc.UniverseFilter)
    assert isinstance(tal1.filters[1], openmc.DelayedGroupFilter)
    assert tal1.scores[0] == 'decay-rate'

    assert isinstance(tal2.filters[0], openmc.UniverseFilter)
    assert isinstance(tal2.filters[1], openmc.EnergyFilter)
    assert tal2.scores[0] == 'nu-fission'

    assert isinstance(tal3.filters[0], openmc.UniverseFilter)
    assert isinstance(tal3.filters[1], openmc.DelayedGroupFilter)
    assert isinstance(tal3.filters[2], openmc.EnergyFilter)
    assert tal3.scores[0] == 'delayed-nu-fission'

    assert tal4.name == 'breeding_ratio_tally'
    assert isinstance(tal4.filters[0], openmc.UniverseFilter)
    assert tal4.scores[0] == '(n,gamma)'
    assert tal4.scores[1] == 'absorption'

    assert tal5.name == 'fission_energy'
    assert isinstance(tal5.filters[0], openmc.UniverseFilter)
    assert tal5.scores[0] == 'kappa-fission'

    assert tal6.name == 'heating'
    assert isinstance(tal6.filters[0], openmc.UniverseFilter)
    assert tal6.scores[0] == 'heating'


def test_read_neutronics_parameters(setup, openmc_depcode):
    mat = openmc.Materials.from_xml(
        openmc_depcode.template_input_file_path['materials'])
    geo = openmc.Geometry.from_xml(
        openmc_depcode.geo_file_paths[0], mat)
    openmc_depcode.write_saltproc_openmc_tallies(mat, geo,
                                                 _DELAYED_ENERGY_BOUNDS, _N_DELAYED_GROUPS)

    old_output_path = openmc_depcode.output_path
    openmc_depcode.output_path = Path(__file__).parents[2] / 'openmc_data/saltproc_runtime_ref'
    openmc_depcode.read_neutronics_parameters()
    np.testing.assert_almost_equal(openmc_depcode.neutronics_parameters['keff_bds'], [1.08350823, 0.00479646])
    np.testing.assert_almost_equal(openmc_depcode.neutronics_parameters['keff_eds'], [1.05103269, 0.00466057])
    np.testing.assert_almost_equal(openmc_depcode.neutronics_parameters['fission_mass_bds'], 72564.3093712)
    np.testing.assert_almost_equal(openmc_depcode.neutronics_parameters['fission_mass_eds'], 72557.3124427)
    np.testing.assert_almost_equal(openmc_depcode.neutronics_parameters['breeding_ratio'], [0.97204677, 0.00752009])
    assert openmc_depcode.neutronics_parameters['power_level'] == 2250000000.0
    assert openmc_depcode.neutronics_parameters['burn_days'] == 3.0
    openmc_depcode.output_path = old_output_path


def test_read_depleted_materials(setup, openmc_depcode):
    old_output_path = openmc_depcode.output_path
    openmc_depcode.output_path = Path(__file__).parents[2] / 'openmc_data/saltproc_runtime_ref'
    xml_mats = openmc.Materials.from_xml(openmc_depcode.output_path / 'depleted_materials.xml')
    xml_mats = dict([(mat.name, mat) for mat in xml_mats if mat.depletable])

    ref_mats = openmc_depcode.read_depleted_materials(True)
    for mat_name, ref_mat in ref_mats.items():
        for nuc in xml_mats[mat_name].get_nuclides():
            np.testing.assert_almost_equal(ref_mat.get_mass(nuc), xml_mats[mat_name].get_mass(nuc))


def test_switch_to_next_geometry(setup, openmc_depcode, openmc_reactor):
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
