"""Test OpenMCDepcode functions"""
import pytest

import numpy as np

import openmc

def test_read_step_metadata(openmc_depcode):
    pass
    #openmc_depcode.read_step_metadata()
    #assert openmc_depcode.step_metadata['depcode_name'] == 'openmc'
    #assert openmc_depcode.step_metadata['depcode_version'] == '2.1.32'
    #assert openmc_depcode.step_metadata['title'] == 'Untitled'
    #assert openmc_depcode.step_metadata['depcode_input_filename'] == \
    #    '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap'
    #assert openmc_depcode.step_metadata['depcode_working_dir'] == \
    #    '/home/andrei2/Desktop/git/saltproc/develop/saltproc'
    #assert openmc_depcode.step_metadata['xs_data_path'] == \
    #    '/home/andrei2/openmc/xsdata/jeff312/sss_jeff312.xsdata'

    #assert openmc_depcode.step_metadata['MPI_tasks'] == 1
    #assert openmc_depcode.step_metadata['OMP_threads'] == 4
    #assert openmc_depcode.step_metadata['memory_optimization_mode'] == 4
    #assert openmc_depcode.step_metadata['depletion_timestep'] == 3.0
    #assert openmc_depcode.step_metadata['memory_usage'] == [10552.84]
    #assert openmc_depcode.step_metadata['execution_time'] == [81.933]


def test_read_neutronics_parameters(openmc_depcode):
    pass
    #openmc_depcode.read_neutronics_parameters()
    #assert openmc_depcode.neutronics_parameters['keff_bds'][0] == 1.00651e+00
    #assert openmc_depcode.neutronics_parameters['keff_eds'][0] == 1.00569e+00
    #assert openmc_depcode.neutronics_parameters['fission_mass_bds'] == [70081]
    #assert openmc_depcode.neutronics_parameters['fission_mass_eds'] == [70077.1]
    #assert openmc_depcode.neutronics_parameters['breeding_ratio'][1] == 5.20000e-04


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
   nameless_matfile = str(cwd / 'openmc_data' / 'tap_materials_nameless.xml')
   # should pass
   openmc_depcode._check_for_material_names(matfile)

   with pytest.raises(ValueError, match="Material 2 has no name."):
       openmc_depcode._check_for_material_names(nameless_matfile)


def test_create_mass_percents_dictionary(cwd, openmc_depcode):
    wo_matfile = str(cwd / 'openmc_data' / 'tap_materials_wo.xml')
    ao_matfile = str(cwd / 'openmc_data' / 'tap_materials_ao.xml')


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
        zai = list(map(openmc.data.zam, nucs))
        zam = list(map(openmc_depcode._z_a_m_to_zam, zai))
        wo_ref_dictionary = dict(zip(zam, mass_percents))

        for key in wo_ref_dictionary.keys():
            np.testing.assert_almost_equal(wo_ref_dictionary[key], wo_test_dictionary[key], decimal=5)


def test_z_a_m_to_zam(openmc_depcode):
    assert openmc_depcode._z_a_m_to_zam((1,1,0)) == 1001
    assert openmc_depcode._z_a_m_to_zam((92,238,0)) == 92238
    assert openmc_depcode._z_a_m_to_zam((47,110,1)) == 47510
    assert openmc_depcode._z_a_m_to_zam((95,242,1)) == 95242
    assert openmc_depcode._z_a_m_to_zam((95,242,0)) == 95642
