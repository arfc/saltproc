from __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent
from saltproc import app
import os
import sys
import numpy as np
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
input_file = directory+'/test'
main_input = directory+'/test.json'
dot_input = directory+'/test.dot'

serpent = DepcodeSerpent(exec_path='sss2',
                         template_fname=directory+'/template.inp',
                         input_fname=input_file,
                         iter_matfile=directory+'/material',
                         geo_file=None)


def test_read_main_input():
    app.read_main_input(main_input)
    assert app.neutron_pop == 50
    assert app.active_cycles == 20
    assert app.active_cycles == 20
    assert app.db_file == directory + '/./db_saltproc.h5'
    assert app.geo_file == ['347_base.ini']
    assert app.restart_flag is False
    np.testing.assert_equal(app.power_hist, [1.250E+9, 1.250E+9])
    np.testing.assert_equal(app.depl_hist, [5, 10])


def test_read_processes_from_input():
    app.read_main_input(main_input)
    procs = app.read_processes_from_input()
    assert procs['fuel']['heat_exchanger'].volume == 1.37E+7
    assert procs['fuel']['sparger'].efficiency['H'] == 0.6
    assert procs['fuel']['sparger'].efficiency['Kr'] == 0.6
    assert procs['fuel']['sparger'].efficiency['Xe'] == 0.6
    assert procs['fuel']['entrainment_separator'].efficiency['H'] == 0.15
    assert procs['fuel']['entrainment_separator'].efficiency['Kr'] == 0.87
    assert procs['ctrlPois']['removal_tb_dy'].volume == 11.0
    assert procs['ctrlPois']['removal_tb_dy'].efficiency['Tb'] == 0
    assert procs['ctrlPois']['removal_tb_dy'].efficiency['Dy'] == 0


def test_read_feeds_from_input():
    app.read_main_input(main_input)
    feeds = app.read_feeds_from_input()
    assert feeds['fuel']['leu'].mass == 4.9602E+8
    assert feeds['fuel']['leu'].density == 4.9602
    assert feeds['fuel']['leu']['U235'] == 15426147.398592
    assert feeds['fuel']['leu']['U238'] == 293096800.37484


def test_read_dot():
    burnable_mat, paths = app.read_dot(dot_input)
    assert burnable_mat == 'fuel'
    assert paths[0][1] == 'sparger'
    assert paths[1][-2] == 'heat_exchanger'
    assert np.shape(paths) == (2, 7)


def test_reprocessing():
    mats = serpent.read_dep_comp(input_file, 1)
    waste_st, rem_mass = app.reprocessing(mats)
    assert rem_mass['fuel'] == 1401.0846504569054
    assert rem_mass['ctrlPois'] == 0.0
    assert waste_st['fuel']['waste_sparger']['Xe135'] == 11.878661583083327
    assert waste_st['fuel']['waste_nickel_filter']['I135'] == 0.90990472940444
    assert waste_st['fuel']['waste_liquid_metal']['Sr90'] == 0.7486923392931839


def test_refill():
    mats = serpent.read_dep_comp(input_file, 1)
    waste_st, rem_mass = app.reprocessing(mats)
    m_after_refill = app.refill(mats, rem_mass, waste_st)
    assert m_after_refill['fuel']['feed_leu']['U235'] == 43.573521906078334
    assert m_after_refill['fuel']['feed_leu']['U238'] == 827.8969156550545
    assert m_after_refill['fuel']['feed_leu']['F19'] == 461.8575149906222
    assert m_after_refill['fuel']['feed_leu']['Li7'] == 67.75331008246572
