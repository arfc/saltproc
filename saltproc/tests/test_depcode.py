from __future__ import absolute_import, division, print_function
from saltproc import Depcode
import os
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))

# global class object
directory = os.path.dirname(path)

serpent = Depcode(codename='SERPENT',
                  exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
                  template_fname=directory+'/template.inp',
                  input_fname=directory+'/test',
                  output_fname='NONE',
                  iter_matfile=directory+'/material',
                  geo_file=[2,
                            os.path.join(directory, '../test_geo.inp')])


def test_get_tra_or_dec():
    serpent.get_tra_or_dec()
    # print(serpent.iso_map)
    assert serpent.iso_map[380880] == '38088.09c'
    assert serpent.iso_map[962400] == '96240.09c'
    assert serpent.iso_map[952421] == '95342.09c'
    assert serpent.iso_map[340831] == '340831'
    assert serpent.iso_map[300732] == '300732'
    assert serpent.iso_map[511262] == '511262'
    assert serpent.iso_map[420931] == '420931'
    assert serpent.iso_map[410911] == '410911'


def test_sss_meta_zzz():
    assert serpent.sss_meta_zzz(47310) == 471101
    assert serpent.sss_meta_zzz(95342) == 952421
    assert serpent.sss_meta_zzz(61348) == 611481
    assert serpent.sss_meta_zzz(52327) == 521271
    assert serpent.sss_meta_zzz(1001) == 1001
    assert serpent.sss_meta_zzz(1002) == 1002
    assert serpent.sss_meta_zzz(48315) == 481151


def test_read_depcode_template():
    template_str = serpent.read_depcode_template(serpent.template_fname)
    # print(template_str)
    assert template_str[18] == 'set pop 30 20 10\n'
    assert template_str[22] == 'set bumode  2\n'
    assert template_str[23] == 'set pcc     1\n'
    assert template_str[28] == 'set power 1.250E+09 dep daytot 3\n'


def test_change_sim_par():
    serpent.npop = 1111
    serpent.active_cycles = 101
    serpent.inactive_cycles = 33
    out = serpent.change_sim_par(
                    serpent.read_depcode_template(serpent.template_fname)
                    )
    # print(out)
    assert out[18] == 'set pop %i %i %i\n' % (
                                              serpent.npop,
                                              serpent.active_cycles,
                                              serpent.inactive_cycles)


def test_get_nuc_name():
    assert serpent.get_nuc_name('92235.09c')[0] == 'U235'
    assert serpent.get_nuc_name('38088.09c')[0] == 'Sr88'
    assert serpent.get_nuc_name('95342.09c')[0] == 'Am242m1'
    assert serpent.get_nuc_name('61348.03c')[0] == 'Pm148m1'
    assert serpent.get_nuc_name('20060')[0] == 'He6'
    assert serpent.get_nuc_name('110241')[0] == 'Na24m1'
    assert serpent.get_nuc_name('170381')[0] == 'Cl38m1'
    assert serpent.get_nuc_name('310741')[0] == 'Ga74m1'
    assert serpent.get_nuc_name('290702')[0] == 'Cu70m2'
    assert serpent.get_nuc_name('250621')[0] == 'Mn62m1'
    assert serpent.get_nuc_name('300732')[0] == 'Zn73m2'
    assert serpent.get_nuc_name('370981')[0] == 'Rb98m1'
    assert serpent.get_nuc_name('390972')[0] == 'Y97m2'
    assert serpent.get_nuc_name('491142')[0] == 'In114m2'


def test_read_depcode_info():
    serpent.read_depcode_info()
    # print(serpent.sim_info)
    assert serpent.sim_info['serpent_version'] == 'Serpent 2.1.31'
    assert serpent.sim_info['title'] == 'Untitled'
    assert serpent.sim_info['MPI_tasks'] == 1
    assert serpent.sim_info['OMP_threads'] == 4
    assert serpent.sim_info['memory_optimization_mode'] == 4


def test_read_depcode_step_param():
    serpent.read_depcode_step_param()
    # print(serpent.param)
    # print(serpent.param['keff_bds'][0][0])
    assert serpent.param['memory_usage'] == [10552.84]
    assert serpent.param['execution_time'] == [81.933]
    assert serpent.param['keff_bds'][0] == 1.00651e+00
    assert serpent.param['keff_eds'][0] == 1.00569e+00
    assert serpent.param['fission_mass_bds'] == [70081]
    assert serpent.param['fission_mass_eds'] == [70077.1]
    assert serpent.param['breeding_ratio'][1] == 5.20000e-04


def test_read_dep_comp():
    mats = serpent.read_dep_comp(serpent.input_fname, 1)
    assert mats['fuel']['U235'] == 3499538.3359278883
    assert mats['fuel']['U238'] == 66580417.24509208
    assert mats['fuel']['F19'] == 37145139.35897285
    assert mats['fuel']['Li7'] == 5449107.821098938
    assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    assert mats['fuel']['Pu239'] == 1231.3628804629795
    assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    assert mats['ctrlPois']['O16'] == 15350.701473655872


def test_write_mat_file():
    mats = serpent.read_dep_comp(serpent.input_fname, 1)
    mat_file = serpent.input_fname + '.mat'
    serpent.write_mat_file(mats, mat_file)
    mat_str = serpent.read_depcode_template(mat_file)
    assert mat_str[0] == '% Material compositions (after 12.000000 days)\n'
    if 'fuel' in mat_str[3]:
        assert mat_str[3].split()[-1] == '2.27175E+07'
        assert mat_str[3].split()[2] == '-4.960200000E+00'
        assert mat_str[1663].split()[-1] == '1.11635E+04'
        assert mat_str[1664] == '            1001.09c  -1.21000137902945E-35\n'
    elif 'ctrlPois' in mat_str[3]:
        assert mat_str[3].split()[-1] == '1.11635E+04'
        assert mat_str[4] == '            1001.09c  -1.21000137902945E-35\n'
    os.remove(mat_file)


def test_insert_path_to_geometry():
    d = serpent.read_depcode_template(serpent.template_fname)
    d_new = serpent.insert_path_to_geometry(d)
    assert d_new[2].split('/')[-1] == 'test_geo.inp"\n'
