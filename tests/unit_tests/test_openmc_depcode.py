"""Test OpenMCDepcode functions"""
import pytest

import numpy as np

import openmc

def test_read_step_metadata(openmc_depcode):
    ## NEED TO CREATE STATEPOINT AND DEPELTION RESULTS FILES
    openmc_depcode.read_step_metadata()
    assert openmc_depcode.step_metadata['depcode_name'] == 'openmc'
    assert openmc_depcode.step_metadata['depcode_version'] == '0.13.2'
    assert openmc_depcode.step_metadata['title'] == ''
    assert openmc_depcode.step_metadata['depcode_input_filename'] == ''
    assert openmc_depcode.step_metadata['depcode_working_dir'] == \
        '/home/ooblack/projects/saltproc/tests/openmc_data/saltproc_runtime'
    assert openmc_depcode.step_metadata['xs_data_path'] == \
        '/home/ooblack/projects/cross-section-librares/endfb71_hdf5/cross_sections.xml'
    assert openmc_depcode.step_metadata['MPI_tasks'] == -1
    assert openmc_depcode.step_metadata['OMP_threads'] == -1
    assert openmc_depcode.step_metadata['memory_optimization_mode'] == -1
    assert openmc_depcode.step_metadata['depletion_timestep'] == 3.0
    assert openmc_depcode.step_metadata['memory_usage'] == [-1]
    assert openmc_depcode.step_metadata['execution_time'] == [81.933] # need to get this value


def test_read_neutronics_parameters(openmc_depcode):
    openmc_depcode.read_neutronics_parameters()
    # NEED TO GET THESE VALUES AND EXPAND THE TEST
    assert openmc_depcode.neutronics_parameters['keff_bds'][0] == 1.00651e+00
    assert openmc_depcode.neutronics_parameters['keff_eds'][0] == 1.00569e+00
    assert openmc_depcode.neutronics_parameters['fission_mass_bds'] == [70081]
    assert openmc_depcode.neutronics_parameters['fission_mass_eds'] == [70077.1]
    assert openmc_depcode.neutronics_parameters['breeding_ratio'][1] == 5.20000e-04


def test_read_depleted_materials(openmc_depcode):
    pass
    #mats = openmc_depcode.read_depleted_materials(True)
    #assert mats['fuel']['U235'] == 3499538.3359278883
    #assert mats['fuel']['U238'] == 66580417.24509208
    #assert mats['fuel']['F19'] == 37145139.35897285
    #assert mats['fuel']['Li7'] == 5449107.821098938
    #assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    #assert mats['fuel']['Pu239'] == 1231.3628804629795
    #assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    #assert mats['ctrlPois']['O16'] == 15350.701473655872


def test_check_for_material_names(cwd, openmc_depcode):
   matfile = openmc_depcode.template_input_file_path['materials']
   nameless_matfile = str(cwd / 'openmc_data' / 'msbr_materials_nameless.xml')
   # should pass
   openmc_depcode._check_for_material_names(matfile)

   with pytest.raises(ValueError, match="Material 2 has no name."):
       openmc_depcode._check_for_material_names(nameless_matfile)


def test_create_mass_percents_dictionary(cwd, openmc_depcode):
    wo_matfile = str(cwd / 'openmc_data' / 'msbr_materials_wo.xml')
    ao_matfile = str(cwd / 'openmc_data' / 'msbr_materials_ao.xml')


    wo_materials = openmc.Materials.from_xml(wo_matfile)
    ao_materials = openmc.Materials.from_xml(ao_matfile)

    for idx, ao_material in enumerate(ao_materials):
        wo_test_dictionary = openmc_depcode._create_mass_percents_dictionary(ao_material)

        wo_material = wo_materials[idx]
        mass_percents = []
        nucs = []
        for nuc, pt, tp in wo_material.nuclides:
            nucs.append(nuc)
            mass_percents.append(pt)
        nucnames = list(map(openmc_depcode._convert_nucname_to_pyne, nucs))
        wo_ref_dictionary = dict(zip(nucnames, mass_percents))

        for key in wo_ref_dictionary.keys():
            np.testing.assert_almost_equal(wo_ref_dictionary[key], wo_test_dictionary[key], decimal=5)


def test_convert_nucname_to_pyne(openmc_depcode):
    assert openmc_depcode._convert_nucname_to_pyne('H1') == 1001
    assert openmc_depcode._convert_nucname_to_pyne('U238') == 92238
    assert openmc_depcode._convert_nucname_to_pyne('Ag110_m1') == 47510
    assert openmc_depcode._convert_nucname_to_pyne('Am242') == 95242
    assert openmc_depcode._convert_nucname_to_pyne('Am242_m1') == 95642
