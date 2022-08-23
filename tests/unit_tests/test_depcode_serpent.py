"""Test SerpentDepcode functions"""
import pytest
import numpy as np

from saltproc import DepcodeSerpent

def test_create_nuclide_name_map_zam_to_serpent(depcode_serpent):
    depcode_serpent.create_nuclide_name_map_zam_to_serpent()
    assert depcode_serpent.iso_map[380880] == '38088.09c'
    assert depcode_serpent.iso_map[962400] == '96240.09c'
    assert depcode_serpent.iso_map[952421] == '95342.09c'
    assert depcode_serpent.iso_map[340831] == '340831'
    assert depcode_serpent.iso_map[300732] == '300732'
    assert depcode_serpent.iso_map[511262] == '511262'
    assert depcode_serpent.iso_map[420931] == '420931'
    assert depcode_serpent.iso_map[410911] == '410911'


def test_convert_nuclide_name_serpent_to_zam(depcode_serpent):
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(47310) == 471101
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(95342) == 952421
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(61348) == 611481
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(52327) == 521271
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(1001) == 1001
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(1002) == 1002
    assert depcode_serpent.convert_nuclide_name_serpent_to_zam(48315) == 481151


def test_read_plaintext_file(depcode_serpent):
    template_str = depcode_serpent.read_plaintext_file(
        depcode_serpent.template_input_file_path)
    assert template_str[6] == '%therm zrh_h 900 hzr05.32t hzr06.32t\n'
    assert template_str[18] == 'set pop 30 20 10\n'
    assert template_str[22] == 'set bumode  2\n'
    assert template_str[23] == 'set pcc     1\n'


def test_get_nuc_name(depcode_serpent):
    assert depcode_serpent.get_nuc_name('92235.09c')[0] == 'U235'
    assert depcode_serpent.get_nuc_name('38088.09c')[0] == 'Sr88'
    assert depcode_serpent.get_nuc_name('95342.09c')[0] == 'Am242m1'
    assert depcode_serpent.get_nuc_name('61348.03c')[0] == 'Pm148m1'
    assert depcode_serpent.get_nuc_name('20060')[0] == 'He6'
    assert depcode_serpent.get_nuc_name('110241')[0] == 'Na24m1'
    assert depcode_serpent.get_nuc_name('170381')[0] == 'Cl38m1'
    assert depcode_serpent.get_nuc_name('310741')[0] == 'Ga74m1'
    assert depcode_serpent.get_nuc_name('290702')[0] == 'Cu70m2'
    assert depcode_serpent.get_nuc_name('250621')[0] == 'Mn62m1'
    assert depcode_serpent.get_nuc_name('300732')[0] == 'Zn73m2'
    assert depcode_serpent.get_nuc_name('370981')[0] == 'Rb98m1'
    assert depcode_serpent.get_nuc_name('390972')[0] == 'Y97m2'
    assert depcode_serpent.get_nuc_name('491142')[0] == 'In114m2'


def test_read_depcode_info(depcode_serpent):
    depcode_serpent.read_depcode_info()
    assert depcode_serpent.sim_info['depcode_name'] == 'Serpent'
    assert depcode_serpent.sim_info['depcode_version'] == '2.1.31'
    assert depcode_serpent.sim_info['title'] == 'Untitled'
    assert depcode_serpent.sim_info['depcode_input_filename'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap'
    assert depcode_serpent.sim_info['depcode_working_dir'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc'
    assert depcode_serpent.sim_info['xs_data_path'] == \
        '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata'

    assert depcode_serpent.sim_info['MPI_tasks'] == 1
    assert depcode_serpent.sim_info['OMP_threads'] == 4
    assert depcode_serpent.sim_info['memory_optimization_mode'] == 4
    assert depcode_serpent.sim_info['depletion_timestep'] == 3.0


def test_read_depcode_step_param(depcode_serpent):
    depcode_serpent.read_depcode_step_param()
    assert depcode_serpent.param['memory_usage'] == [10552.84]
    assert depcode_serpent.param['execution_time'] == [81.933]
    assert depcode_serpent.param['keff_bds'][0] == 1.00651e+00
    assert depcode_serpent.param['keff_eds'][0] == 1.00569e+00
    assert depcode_serpent.param['fission_mass_bds'] == [70081]
    assert depcode_serpent.param['fission_mass_eds'] == [70077.1]
    assert depcode_serpent.param['breeding_ratio'][1] == 5.20000e-04


def test_read_dep_comp(depcode_serpent):
    mats = depcode_serpent.read_dep_comp(True)
    assert mats['fuel']['U235'] == 3499538.3359278883
    assert mats['fuel']['U238'] == 66580417.24509208
    assert mats['fuel']['F19'] == 37145139.35897285
    assert mats['fuel']['Li7'] == 5449107.821098938
    assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    assert mats['fuel']['Pu239'] == 1231.3628804629795
    assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    assert mats['ctrlPois']['O16'] == 15350.701473655872
