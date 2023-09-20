"""Test SerpentDepcode functions"""
import pytest
import numpy as np
import tempfile
from pathlib import Path

from saltproc import SerpentDepcode


def test_create_nuclide_name_map_zam_to_serpent(serpent_depcode, cwd):
    old_runtime_inputfile = serpent_depcode.runtime_inputfile
    nuc_code_map = serpent_depcode.map_nuclide_name_to_serpent_name()
    assert nuc_code_map['Sr88'] == '38088.09c'
    assert nuc_code_map['Cm240'] == '96240.09c'
    assert nuc_code_map['Am242_m1'] == '95342.09c'
    assert nuc_code_map['Se83_m1'] == '340831'
    assert nuc_code_map['Zn73_m2'] == '300732'
    assert nuc_code_map['Sb126_m2'] == '511262'
    assert nuc_code_map['Mo93_m1'] == '420931'
    assert nuc_code_map['Nb91_m1'] == '410911'

    serpent_depcode.zaid_convention = 'mcnp'
    serpent_depcode.runtime_inputfile = str(cwd / 'serpent_data' / 'tap_reference_mcnp')
    nuc_code_map = serpent_depcode.map_nuclide_name_to_serpent_name()
    assert nuc_code_map['Sr88'] == '38088.82c'
    assert nuc_code_map['Cm240'] == '96240.82c'
    assert nuc_code_map['Am242_m1'] == '95642.82c'
    assert nuc_code_map['Am242'] == '95242.82c'
    assert nuc_code_map['Ag110_m1'] == '47510.82c'
    assert nuc_code_map['Se83_m1'] == '340831'
    assert nuc_code_map['Zn73_m2'] == '300732'
    assert nuc_code_map['Sb126_m2'] == '511262'
    assert nuc_code_map['Mo93_m1'] == '420931'
    assert nuc_code_map['Nb91_m1'] == '410911'

    serpent_depcode.zaid_convention = 'nndc'
    serpent_depcode.runtime_inputfile = str(cwd / 'serpent_data' / 'tap_reference_nndc')
    nuc_code_map = serpent_depcode.map_nuclide_name_to_serpent_name()

    assert nuc_code_map['Sr88'] == '38088.82c'
    assert nuc_code_map['Cm240'] == '96240.82c'
    assert nuc_code_map['Am242_m1'] == '95242.82c'
    assert nuc_code_map['Am242'] == '95642.82c'
    assert nuc_code_map['Ag110_m1'] == '47510.82c'
    assert nuc_code_map['Se83_m1'] == '340831'
    assert nuc_code_map['Zn73_m2'] == '300732'
    assert nuc_code_map['Sb126_m2'] == '511262'
    assert nuc_code_map['Mo93_m1'] == '420931'
    assert nuc_code_map['Nb91_m1'] == '410911'

    serpent_depcode.runtime_inputfile = old_runtime_inputfile
    serpent_depcode.zaid_convention = 'serpent'


def test_nuclide_code_to_zam(serpent_depcode):
    assert serpent_depcode._nuclide_code_to_zam(47310) == (47, 110, 1)
    assert serpent_depcode._nuclide_code_to_zam(95342) == (95, 242, 1)
    assert serpent_depcode._nuclide_code_to_zam(61348) == (61, 148, 1)
    assert serpent_depcode._nuclide_code_to_zam(52327) == (52, 127, 1)
    assert serpent_depcode._nuclide_code_to_zam(1001) == (1, 1, 0)
    assert serpent_depcode._nuclide_code_to_zam(1002) == (1, 2, 0)
    assert serpent_depcode._nuclide_code_to_zam(48315) == (48, 115, 1)


def test_get_neutron_settings(serpent_depcode):
    template_str = serpent_depcode.read_plaintext_file(
        serpent_depcode.template_input_file_path)
    serpent_depcode.get_neutron_settings(template_str)
    assert serpent_depcode.npop == 50
    assert serpent_depcode.active_cycles == 20
    assert serpent_depcode.inactive_cycles == 20

def test_get_burnable_materials_file(serpent_depcode):
    err1 = (f'Template file {serpent_depcode.template_input_file_path}'
            ' has no <include "material_file"> statements')

    with pytest.raises(IOError, match=err1):
        lines_no_include = ['this line does not start with include']
        serpent_depcode._get_burnable_materials_file(lines_no_include)

    with tempfile.NamedTemporaryFile(mode='w+') as tf:
        tf.write('some junk')
        old_template = serpent_depcode.template_input_file_path
        serpent_depcode.template_input_file_path = tf.name

        err2 = (f'Template file {serpent_depcode.template_input_file_path}'
                ' includes no file with materials description')
        with pytest.raises(IOError, match=err2):
            lines_bad_matfile = [f'include "{tf.name}"']
            serpent_depcode._get_burnable_materials_file(lines_bad_matfile)
        serpent_depcode.template_input_file_path = old_template

def test_get_burnable_material_card_data(serpent_depcode):
    bad_mat_cards = ['mat fuel -9.2 burn 1 fix 09c',
                     'mat blanket -9.1 burn 1']

    err = ('"mat" card for burnable material "blanket" does not have a "fix"'
           ' option. Burnable materials in SaltProc must include the "fix"'
           ' option. See the serpent wiki for more information:'
           ' https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#mat')
    with pytest.raises(IOError, match=err):
        serpent_depcode._get_burnable_material_card_data(bad_mat_cards)


def test_read_plaintext_file(serpent_depcode):
    template_str = serpent_depcode.read_plaintext_file(
        serpent_depcode.template_input_file_path)
    assert template_str[6] == '%therm zrh_h 900 hzr05.32t hzr06.32t\n'
    assert template_str[18] == 'set pop 50 20 20\n'
    assert template_str[22] == 'set bumode  2\n'
    assert template_str[23] == 'set pcc     1\n'


def test_nuclide_code_to_name(serpent_depcode):
    assert serpent_depcode.nuclide_code_to_name('92235.09c') == 'U235'
    assert serpent_depcode.nuclide_code_to_name('38088.09c') == 'Sr88'
    assert serpent_depcode.nuclide_code_to_name('95342.09c') == 'Am242_m1'
    assert serpent_depcode.nuclide_code_to_name('61348.03c') == 'Pm148_m1'
    assert serpent_depcode.nuclide_code_to_name('20060') == 'He6'
    assert serpent_depcode.nuclide_code_to_name('110241') == 'Na24_m1'
    assert serpent_depcode.nuclide_code_to_name('170381') == 'Cl38_m1'
    assert serpent_depcode.nuclide_code_to_name('310741') == 'Ga74_m1'
    assert serpent_depcode.nuclide_code_to_name('290702') == 'Cu70_m2'
    assert serpent_depcode.nuclide_code_to_name('250621') == 'Mn62_m1'
    assert serpent_depcode.nuclide_code_to_name('300732') == 'Zn73_m2'
    assert serpent_depcode.nuclide_code_to_name('370981') == 'Rb98_m1'
    assert serpent_depcode.nuclide_code_to_name('390972') == 'Y97_m2'
    assert serpent_depcode.nuclide_code_to_name('491142') == 'In114_m2'

    serpent_depcode.zaid_convention = 'mcnp'
    assert serpent_depcode.nuclide_code_to_name('92235.82c') == 'U235'
    assert serpent_depcode.nuclide_code_to_name('38088.82c') == 'Sr88'
    assert serpent_depcode.nuclide_code_to_name('95642.82c') == 'Am242_m1'
    assert serpent_depcode.nuclide_code_to_name('95242.82c') == 'Am242'
    assert serpent_depcode.nuclide_code_to_name('61548.82c') == 'Pm148_m1'
    assert serpent_depcode.nuclide_code_to_name('20060') == 'He6'
    assert serpent_depcode.nuclide_code_to_name('110241') == 'Na24_m1'
    assert serpent_depcode.nuclide_code_to_name('170381') == 'Cl38_m1'
    assert serpent_depcode.nuclide_code_to_name('310741') == 'Ga74_m1'
    assert serpent_depcode.nuclide_code_to_name('290702') == 'Cu70_m2'
    assert serpent_depcode.nuclide_code_to_name('250621') == 'Mn62_m1'
    assert serpent_depcode.nuclide_code_to_name('300732') == 'Zn73_m2'
    assert serpent_depcode.nuclide_code_to_name('370981') == 'Rb98_m1'
    assert serpent_depcode.nuclide_code_to_name('390972') == 'Y97_m2'
    assert serpent_depcode.nuclide_code_to_name('491142') == 'In114_m2'

    serpent_depcode.zaid_convention = 'nndc'
    assert serpent_depcode.nuclide_code_to_name('92235.82c') == 'U235'
    assert serpent_depcode.nuclide_code_to_name('38088.82c') == 'Sr88'
    assert serpent_depcode.nuclide_code_to_name('95242.82c') == 'Am242_m1'
    assert serpent_depcode.nuclide_code_to_name('95642.82c') == 'Am242'
    assert serpent_depcode.nuclide_code_to_name('61548.82c') == 'Pm148_m1'
    assert serpent_depcode.nuclide_code_to_name('20060') == 'He6'
    assert serpent_depcode.nuclide_code_to_name('110241') == 'Na24_m1'
    assert serpent_depcode.nuclide_code_to_name('170381') == 'Cl38_m1'
    assert serpent_depcode.nuclide_code_to_name('310741') == 'Ga74_m1'
    assert serpent_depcode.nuclide_code_to_name('290702') == 'Cu70_m2'
    assert serpent_depcode.nuclide_code_to_name('250621') == 'Mn62_m1'
    assert serpent_depcode.nuclide_code_to_name('300732') == 'Zn73_m2'
    assert serpent_depcode.nuclide_code_to_name('370981') == 'Rb98_m1'
    assert serpent_depcode.nuclide_code_to_name('390972') == 'Y97_m2'
    assert serpent_depcode.nuclide_code_to_name('491142') == 'In114_m2'

    serpent_depcode.zaid_convention = 'serpent'


def test_read_depcode_metadata(serpent_depcode):
    serpent_depcode.read_depcode_metadata()
    assert serpent_depcode.depcode_metadata['depcode_name'] == 'Serpent'
    assert serpent_depcode.depcode_metadata['depcode_version'] == '2.1.31'
    assert serpent_depcode.depcode_metadata['title'] == 'Untitled'
    assert serpent_depcode.depcode_metadata['depcode_input_filename'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap'
    assert serpent_depcode.depcode_metadata['depcode_working_dir'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc'
    assert serpent_depcode.depcode_metadata['xs_data_path'] == \
        '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata'


def test_read_step_metadata(serpent_depcode):
    serpent_depcode.read_step_metadata()
    assert serpent_depcode.step_metadata['MPI_tasks'] == 1
    assert serpent_depcode.step_metadata['OMP_threads'] == 4
    assert serpent_depcode.step_metadata['memory_optimization_mode'] == 4
    assert serpent_depcode.step_metadata['depletion_timestep_size'] == 3.0
    assert serpent_depcode.step_metadata['step_memory_usage'] == 10552.8
    assert serpent_depcode.step_metadata['step_execution_time'] == 111.76060000000001


def test_read_neutronics_parameters(serpent_depcode):
    serpent_depcode.read_neutronics_parameters()
    assert serpent_depcode.neutronics_parameters['keff_bds'][0] == 1.00651
    assert serpent_depcode.neutronics_parameters['keff_eds'][0] == 1.00569
    assert serpent_depcode.neutronics_parameters['fission_mass_bds'] == [70081]
    assert serpent_depcode.neutronics_parameters['fission_mass_eds'] == [70077.1]
    assert serpent_depcode.neutronics_parameters['breeding_ratio_eds'][1] == 5.2e-04
    assert serpent_depcode.neutronics_parameters['breeding_ratio_bds'][1] == 5.4e-04
    assert serpent_depcode.neutronics_parameters['burn_days'] == 3.0
    assert serpent_depcode.neutronics_parameters['power_level'] == 1.25e9
    np.testing.assert_equal(serpent_depcode.neutronics_parameters['beta_eff_bds'],
                            [[0.0073977, 0.00324],
                             [0.000217048, 0.01744],
                             [0.00105221, 0.00807],
                             [0.000638056, 0.00979],
                             [0.00139092, 0.0068],
                             [0.00234135, 0.00544],
                             [0.000813505, 0.00916],
                             [0.000680349, 0.00967],
                             [0.000264266, 0.0154]])
    np.testing.assert_equal(serpent_depcode.neutronics_parameters['beta_eff_eds'],
                            [[0.00739026, 0.00312],
                             [0.000219973, 0.01763],
                             [0.00106376, 0.00788],
                             [0.000632466, 0.01052],
                             [0.00139341, 0.00701],
                             [0.00230227, 0.00542],
                             [0.000822292, 0.00841],
                             [0.000685158, 0.01013],
                             [0.000270932, 0.01507]])
    np.testing.assert_equal(serpent_depcode.neutronics_parameters['delayed_neutrons_lambda_bds'],
                            [[4.76145e-01, 4.39000e-03],
                             [1.24667e-02, 0.00000e+00],
                             [2.82917e-02, 4.90000e-09],
                             [4.25244e-02, 7.10000e-09],
                             [1.33042e-01, 0.00000e+00],
                             [2.92467e-01, 0.00000e+00],
                             [6.66488e-01, 0.00000e+00],
                             [1.63478e+00, 5.20000e-09],
                             [3.55460e+00, 0.00000e+00]])
    np.testing.assert_equal(serpent_depcode.neutronics_parameters['delayed_neutrons_lambda_eds'],
                            [[4.80259e-01, 4.51000e-03],
                             [1.24667e-02, 0.00000e+00],
                             [2.82917e-02, 4.90000e-09],
                             [4.25244e-02, 7.10000e-09],
                             [1.33042e-01, 0.00000e+00],
                             [2.92467e-01, 0.00000e+00],
                             [6.66488e-01, 0.00000e+00],
                             [1.63478e+00, 5.20000e-09],
                             [3.55460e+00, 0.00000e+00]])
    assert serpent_depcode.neutronics_parameters['fission_mass_bds'] == 70081.
    assert serpent_depcode.neutronics_parameters['fission_mass_eds'] == 70077.1


def test_read_depleted_materials(serpent_depcode):
    mats = serpent_depcode.read_depleted_materials(True)
    np.testing.assert_allclose(mats['fuel'].get_mass('U235'), 3499538.3359278883, rtol=1e-6)
    np.testing.assert_allclose(mats['fuel'].get_mass('U238'), 66580417.24509208, rtol=1e-6)
    np.testing.assert_allclose(mats['fuel'].get_mass('F19'), 37145139.35897285, rtol=1e-6)
    np.testing.assert_allclose(mats['fuel'].get_mass('Li7'), 5449107.821098938, rtol=1e-6)
    np.testing.assert_allclose(mats['fuel'].get_mass('Cm240'), 8.787897203694538e-22, rtol=1e-6)
    np.testing.assert_allclose(mats['fuel'].get_mass('Pu239'), 1231.3628804629795, rtol=1e-6)
    np.testing.assert_allclose(mats['ctrlPois'].get_mass('Gd155'), 5812.83289505528, rtol=1e-6)
    np.testing.assert_allclose(mats['ctrlPois'].get_mass('O16'), 15350.701473655872, rtol=1e-6)
