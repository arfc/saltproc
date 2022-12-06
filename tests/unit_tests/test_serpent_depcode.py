"""Test SerpentDepcode functions"""
import pytest
import numpy as np

from saltproc import SerpentDepcode


def test_create_nuclide_name_map_zam_to_serpent(serpent_depcode):
    nuc_code_map = serpent_depcode.map_nuclide_code_zam_to_serpent()
    assert nuc_code_map[380880] == '38088.09c'
    assert nuc_code_map[962400] == '96240.09c'
    assert nuc_code_map[952421] == '95342.09c'
    assert nuc_code_map[340831] == '340831'
    assert nuc_code_map[300732] == '300732'
    assert nuc_code_map[511262] == '511262'
    assert nuc_code_map[420931] == '420931'
    assert nuc_code_map[410911] == '410911'


def test_convert_nuclide_code_to_zam(serpent_depcode):
    assert serpent_depcode.convert_nuclide_code_to_zam(47310) == 471101
    assert serpent_depcode.convert_nuclide_code_to_zam(95342) == 952421
    assert serpent_depcode.convert_nuclide_code_to_zam(61348) == 611481
    assert serpent_depcode.convert_nuclide_code_to_zam(52327) == 521271
    assert serpent_depcode.convert_nuclide_code_to_zam(1001) == 1001
    assert serpent_depcode.convert_nuclide_code_to_zam(1002) == 1002
    assert serpent_depcode.convert_nuclide_code_to_zam(48315) == 481151


def test_get_neutron_settings(serpent_depcode):
    template_str = serpent_depcode.read_plaintext_file(
        serpent_depcode.template_input_file_path)
    serpent_depcode.get_neutron_settings(template_str)
    assert serpent_depcode.npop == 50
    assert serpent_depcode.active_cycles == 20
    assert serpent_depcode.inactive_cycles == 20


def test_read_plaintext_file(serpent_depcode):
    template_str = serpent_depcode.read_plaintext_file(
        serpent_depcode.template_input_file_path)
    assert template_str[6] == '%therm zrh_h 900 hzr05.32t hzr06.32t\n'
    assert template_str[18] == 'set pop 50 20 20\n'
    assert template_str[22] == 'set bumode  2\n'
    assert template_str[23] == 'set pcc     1\n'


def test_convert_nuclide_code_to_name(serpent_depcode):
    assert serpent_depcode.convert_nuclide_code_to_name('92235.09c') == 'U235'
    assert serpent_depcode.convert_nuclide_code_to_name('38088.09c') == 'Sr88'
    assert serpent_depcode.convert_nuclide_code_to_name('95342.09c') == 'Am242m1'
    assert serpent_depcode.convert_nuclide_code_to_name('61348.03c') == 'Pm148m1'
    assert serpent_depcode.convert_nuclide_code_to_name('20060') == 'He6'
    assert serpent_depcode.convert_nuclide_code_to_name('110241') == 'Na24m1'
    assert serpent_depcode.convert_nuclide_code_to_name('170381') == 'Cl38m1'
    assert serpent_depcode.convert_nuclide_code_to_name('310741') == 'Ga74m1'
    assert serpent_depcode.convert_nuclide_code_to_name('290702') == 'Cu70m2'
    assert serpent_depcode.convert_nuclide_code_to_name('250621') == 'Mn62m1'
    assert serpent_depcode.convert_nuclide_code_to_name('300732') == 'Zn73m2'
    assert serpent_depcode.convert_nuclide_code_to_name('370981') == 'Rb98m1'
    assert serpent_depcode.convert_nuclide_code_to_name('390972') == 'Y97m2'
    assert serpent_depcode.convert_nuclide_code_to_name('491142') == 'In114m2'


def test_read_step_metadata(serpent_depcode):
    serpent_depcode.read_step_metadata()
    assert serpent_depcode.step_metadata['depcode_name'] == 'Serpent'
    assert serpent_depcode.step_metadata['depcode_version'] == '2.1.31'
    assert serpent_depcode.step_metadata['title'] == 'Untitled'
    assert serpent_depcode.step_metadata['depcode_input_filename'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap'
    assert serpent_depcode.step_metadata['depcode_working_dir'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc'
    assert serpent_depcode.step_metadata['xs_data_path'] == \
        '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata'

    assert serpent_depcode.step_metadata['MPI_tasks'] == 1
    assert serpent_depcode.step_metadata['OMP_threads'] == 4
    assert serpent_depcode.step_metadata['memory_optimization_mode'] == 4
    assert serpent_depcode.step_metadata['depletion_timestep'] == 3.0
    assert serpent_depcode.step_metadata['memory_usage'] == [10552.84]
    assert serpent_depcode.step_metadata['execution_time'] == [81.933]


def test_read_neutronics_parameters(serpent_depcode):
    serpent_depcode.read_neutronics_parameters()
    assert serpent_depcode.neutronics_parameters['keff_bds'][0] == 1.00651e+00
    assert serpent_depcode.neutronics_parameters['keff_eds'][0] == 1.00569e+00
    assert serpent_depcode.neutronics_parameters['fission_mass_bds'] == [70081]
    assert serpent_depcode.neutronics_parameters['fission_mass_eds'] == [70077.1]
    assert serpent_depcode.neutronics_parameters['breeding_ratio'][1] == 5.20000e-04


def test_read_depleted_materials(serpent_depcode):
    mats = serpent_depcode.read_depleted_materials(True)
    assert mats['fuel']['U235'] == 3499538.3359278883
    assert mats['fuel']['U238'] == 66580417.24509208
    assert mats['fuel']['F19'] == 37145139.35897285
    assert mats['fuel']['Li7'] == 5449107.821098938
    assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    assert mats['fuel']['Pu239'] == 1231.3628804629795
    assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    assert mats['ctrlPois']['O16'] == 15350.701473655872
