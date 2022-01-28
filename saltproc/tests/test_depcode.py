from __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent
from saltproc import Reactor
import os
import sys
import shutil
import numpy as np

path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))

# global class object
directory = os.path.dirname(path)

serpent = DepcodeSerpent(exec_path='sss2',
                         template_inputfile_path=directory + '/template.inp',
                         iter_inputfile=directory + '/test',
                         iter_matfile=directory + '/material',
                         geo_files=[os.path.join(directory, '../test_geo.inp')])

msr = Reactor(volume=1.0,
              power_levels=[1.250E+09, 1.250E+09, 5.550E+09],
              depl_hist=[111.111, 2101.9, 3987.5])

geo_test_input = directory + '/test_geometry_switch.inp'

def test_get_tra_or_dec():
    serpent.get_tra_or_dec(serpent.iter_inputfile)
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
    template_str = serpent.read_depcode_template(serpent.template_inputfile_path)
    assert template_str[6] == '%therm zrh_h 900 hzr05.32t hzr06.32t\n'
    assert template_str[18] == 'set pop 30 20 10\n'
    assert template_str[22] == 'set bumode  2\n'
    assert template_str[23] == 'set pcc     1\n'


def test_change_sim_par():
    serpent.npop = 1111
    serpent.active_cycles = 101
    serpent.inactive_cycles = 33
    out = serpent.change_sim_par(
        serpent.read_depcode_template(serpent.template_inputfile_path)
    )
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
    assert serpent.sim_info['depcode_name'] == 'Serpent'
    assert serpent.sim_info['depcode_version'] == '2.1.31'
    assert serpent.sim_info['title'] == 'Untitled'
    assert serpent.sim_info['depcode_input_filename'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap'
    assert serpent.sim_info['depcode_working_dir'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc'
    assert serpent.sim_info['xs_data_path'] == \
        '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata'

    assert serpent.sim_info['MPI_tasks'] == 1
    assert serpent.sim_info['OMP_threads'] == 4
    assert serpent.sim_info['memory_optimization_mode'] == 4
    assert serpent.sim_info['depletion_timestep'] == 3.0


def test_read_depcode_step_param():
    serpent.read_depcode_step_param()
    assert serpent.param['memory_usage'] == [10552.84]
    assert serpent.param['execution_time'] == [81.933]
    assert serpent.param['keff_bds'][0] == 1.00651e+00
    assert serpent.param['keff_eds'][0] == 1.00569e+00
    assert serpent.param['fission_mass_bds'] == [70081]
    assert serpent.param['fission_mass_eds'] == [70077.1]
    assert serpent.param['breeding_ratio'][1] == 5.20000e-04


def test_read_dep_comp():
    mats = serpent.read_dep_comp(True)
    assert mats['fuel']['U235'] == 3499538.3359278883
    assert mats['fuel']['U238'] == 66580417.24509208
    assert mats['fuel']['F19'] == 37145139.35897285
    assert mats['fuel']['Li7'] == 5449107.821098938
    assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    assert mats['fuel']['Pu239'] == 1231.3628804629795
    assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    assert mats['ctrlPois']['O16'] == 15350.701473655872


def test_write_mat_file():
    mats = serpent.read_dep_comp(True)
    iter_matfile_old = serpent.iter_matfile
    serpent.iter_inputfile = serpent.iter_inputfile + '.mat'
    serpent.write_mat_file(mats, 12.0)
    mat_str = serpent.read_depcode_template(serpent.iter_matfile)
    assert mat_str[0] == '% Material compositions (after 12.000000 days)\n'
    if 'fuel' in mat_str[3]:
        assert mat_str[3].split()[-1] == '2.27175E+07'
        assert mat_str[3].split()[2] == '-4.960200000E+00'
        assert mat_str[1663].split()[-1] == '1.11635E+04'
        assert mat_str[1664] == '            1001.09c  -1.21000137902945E-35\n'
    elif 'ctrlPois' in mat_str[3]:
        assert mat_str[3].split()[-1] == '1.11635E+04'
        assert mat_str[4] == '            1001.09c  -1.21000137902945E-35\n'
    os.remove(serpent.iter_matfile)
    serpent.iter_matfile = iter_matfile_old


def test_insert_path_to_geometry():
    d = serpent.read_depcode_template(serpent.template_inputfile_path)
    d_new = serpent.insert_path_to_geometry(d)
    assert d_new[5].split('/')[-1] == 'test_geo.inp"\n'


def test_replace_burnup_parameters():
    time = msr.depl_hist.copy()
    time.insert(0, 0.0)
    depsteps = np.diff(time)
    d = serpent.read_depcode_template(serpent.template_inputfile_path)
    for idx in range(len(msr.power_levels)):
        d = serpent.replace_burnup_parameters(d,
                                              msr,
                                              idx)
        out_file = open(serpent.template_inputfile_path + str(idx), 'w')
        out_file.writelines(d)
        out_file.close()
        d_new = serpent.read_depcode_template(
            serpent.template_inputfile_path + str(idx))
        assert d_new[8].split()[4] == 'daystep'
        assert d_new[8].split()[2] == str("%5.9E" % msr.power_levels[idx])
        assert d_new[8].split()[5] == str("%7.5E" % depsteps[idx])
        os.remove(serpent.template_inputfile_path + str(idx))


def test_create_iter_matfile():
    d = serpent.read_depcode_template(serpent.template_inputfile_path)
    out = serpent.create_iter_matfile(d)
    assert out[0].split()[-1] == '\"' + serpent.iter_matfile + '\"'
    os.remove(serpent.iter_matfile)


def test_write_depcode_input():
    iter_inputfile_old = serpent.iter_inputfile
    serpent.iter_inputfile = serpent.iter_inputfile + '_write_test'
    serpent.write_depcode_input(msr,
                                0,
                                False)
    d = serpent.read_depcode_template(serpent.iter_inputfile)
    print(d[0])
    assert d[0].split('/')[-2] == 'tests'
    assert d[0].split('/')[-1] == 'material"\n'
    assert d[8].split()[2] == '1.250000000E+09'
    assert d[8].split()[4] == 'daystep'
    assert d[8].split()[-1] == '1.11111E+02'
    assert d[20] == 'set pop 1111 101 33\n'
    os.remove(serpent.iter_inputfile)
    os.remove(serpent.iter_matfile)

    serpent.iter_inputfile = iter_inputfile_old

def test_switch_to_next_geometry():
    shutil.copy2(geo_test_input, serpent.iter_inputfile + '_test')
    iter_inputfile_old = serpent.iter_inputfile
    serpent.iter_inputfile = serpent.iter_inputfile + '_test'
    serpent.geo_files += ['../../examples/406.inp', '../../examples/988.inp']
    serpent.switch_to_next_geometry()
    d = serpent.read_depcode_template(serpent.iter_inputfile)
    assert d[5].split('/')[-1] == '988.inp"\n'
    os.remove(serpent.iter_inputfile)
    serpent.iter_inputfile = iter_inputfile_old
