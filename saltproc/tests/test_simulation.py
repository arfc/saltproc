from __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent
from saltproc import Simulation
import os
import sys
import shutil
import numpy as np
import tables as tb
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
input_file = directory + '/test'
geo_test_input = directory + '/test_geometry_switch.inp'

serpent = DepcodeSerpent(
    exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
    template_path=directory + '/template.inp',
    input_path=input_file,
    iter_matfile=directory + '/material',
    geo_file=[
        '../../examples/406.inp',
        '../../examples/988.inp'])

simulation = Simulation(sim_name='Simulation unit tests',
                        sim_depcode=serpent,
                        core_number=1,
                        node_number=1,
                        db_path=directory + '/test_db.h5',
                        iter_matfile=serpent.iter_matfile)

#def test_check_switch_geo_trigger()

#def test_store_after_repr()

def test_store_mat_data():
    # read data
    mats_before = simulation.sim_depcode.read_dep_comp(
        simulation.sim_depcode.input_path,
        False)
    mats_after = simulation.sim_depcode.read_dep_comp(
        simulation.sim_depcode.input_path,
        True)

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = serpent.input_path + '.h5'
    simulation.db_path = db_file

    # store data at end
    simulation.store_mat_data(mats_before, 0, False)
    simulation.store_mat_data(mats_after, 0, True)

    # read stored data
    db = tb.open_file(simulation.db_path, mode='r',
                      filters=simulation.compression_params)
    tmats = db.root.materials

    tfuel_before = tmats.fuel.before_reproc.comp[0]
    tfuel_before_params = tmats.fuel.before_reproc.parameters[0]

    tfuel_after = tmats.fuel.after_reproc.comp[0]
    tfuel_after_params = tmats.fuel.after_reproc.parameters[0]

    tpois_before = tmats.ctrlPois.before_reproc.comp[0]
    tpois_before_params = tmats.ctrlPois.before_reproc.parameters[0]

    tpois_after = tmats.ctrlPois.after_reproc.comp[0]
    tpois_after_params = tmats.ctrlPois.after_reproc.parameters[0]

    # Check the mass fractions
    assert mats_before['fuel']['U235'] == tfuel_before[1566]
    assert mats_before['fuel']['U238'] == tfuel_before[1570]
    assert mats_before['fuel']['F19'] == tfuel_before[37]
    assert mats_before['fuel']['Li7'] == tfuel_before[8]
    assert mats_before['fuel']['Cm240'] == tfuel_before[1610]
    assert mats_before['fuel']['Pu239'] == tfuel_before[1589]
    assert mats_before['ctrlPois']['Gd155'] == tpois_before[1213]
    assert mats_before['ctrlPois']['O16'] == tpois_before[32]

    assert mats_after['fuel']['U235'] == tfuel_after[1566]
    assert mats_after['fuel']['U238'] == tfuel_after[1570]
    assert mats_after['fuel']['F19'] == tfuel_after[37]
    assert mats_after['fuel']['Li7'] == tfuel_after[8]
    assert mats_after['fuel']['Cm240'] == tfuel_after[1610]
    assert mats_after['fuel']['Pu239'] == tfuel_after[1589]
    assert mats_after['ctrlPois']['Gd155'] == tpois_after[1213]
    assert mats_after['ctrlPois']['O16'] == tpois_after[32]

    # Check the parameters
    assert mats_before['fuel'].mass == tfuel_before_params[0]
    assert mats_before['fuel'].density == tfuel_before_params[1]
    assert mats_before['fuel'].vol == tfuel_before_params[2]
    assert mats_before['fuel'].temp == tfuel_before_params[3]
    assert mats_before['fuel'].mass_flowrate == tfuel_before_params[4]
    assert mats_before['fuel'].void_frac == tfuel_before_params[5]
    assert mats_before['fuel'].burnup == tfuel_before_params[6]

    assert mats_before['ctrlPois'].mass == tpois_before_params[0]
    assert mats_before['ctrlPois'].density == tpois_before_params[1]
    assert mats_before['ctrlPois'].vol == tpois_before_params[2]
    assert mats_before['ctrlPois'].temp == tpois_before_params[3]
    assert mats_before['ctrlPois'].mass_flowrate == tpois_before_params[4]
    assert mats_before['ctrlPois'].void_frac == tpois_before_params[5]
    assert mats_before['ctrlPois'].burnup == tpois_before_params[6]

    assert mats_after['fuel'].mass == tfuel_after_params[0]
    assert mats_after['fuel'].density == tfuel_after_params[1]
    assert mats_after['fuel'].vol == tfuel_after_params[2]
    assert mats_after['fuel'].temp == tfuel_after_params[3]
    assert mats_after['fuel'].mass_flowrate == tfuel_after_params[4]
    assert mats_after['fuel'].void_frac == tfuel_after_params[5]
    assert mats_after['fuel'].burnup == tfuel_after_params[6]

    assert mats_after['ctrlPois'].mass == tpois_after_params[0]
    assert mats_after['ctrlPois'].density == tpois_after_params[1]
    assert mats_after['ctrlPois'].vol == tpois_after_params[2]
    assert mats_after['ctrlPois'].temp == tpois_after_params[3]
    assert mats_after['ctrlPois'].mass_flowrate == tpois_after_params[4]
    assert mats_after['ctrlPois'].void_frac == tpois_after_params[5]
    assert mats_after['ctrlPois'].burnup == tpois_after_params[6]

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    #use original db path
    simulation.db_path = db_path_old

#def test_store_run_init_info()

#def test_store_run_step_info()


def test_read_k_eds_delta():
    assert simulation.read_k_eds_delta(7, False) is False


def test_switch_to_next_geometry():
    shutil.copy2(geo_test_input, serpent.input_path + '_test')
    serpent.input_path = serpent.input_path + '_test'
    simulation.switch_to_next_geometry()
    d = serpent.read_depcode_template(serpent.input_path)
    assert d[5].split('/')[-1] == '988.inp"\n'
    os.remove(serpent.input_path)
