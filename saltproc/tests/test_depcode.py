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
                  iter_matfile=directory+'/material')


def test_get_tra_or_dec():
    serpent.get_tra_or_dec()
    print(serpent.iso_map)
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
    print(template_str)
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
    print(out)
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
