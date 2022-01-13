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

def test_check_switch_geo_trigger()

def test_store_after_repr()

def test_store_mat_data():
    # read data
    mats_before = simulation.sim_depcode.read_dep_comp(
        simulation.sim_depcode.input_path+,
        False)
    mats_after = simulation.sim_depcode.read_dep_comp(
        simulation.sim_depcode.input_path+,
        True)

    # store data at end
    simulation.store_mat_data(mats_before, -1, False)
    simulation.store_mat_data(mats_after, -1, True)

    # read stored data
    db = tb.open_file(simulation.db_path, mode='r',
                      filters=simulation.compression_params)
    tmats = db.root.materials
    tmats_before = tmats.before_reproc.comp[-1,:]
    tmats_after = tmats.after_reproc.comp[-1,:]

    # check that they match
    assert mats_before['fuel']['U235'] == tmats_before[1566]
    assert mats_before['fuel']['U238'] == tmats_before[1570]
    assert mats_before['fuel']['F19'] == tmats_before[37]
    assert mats_before['fuel']['Li7'] == tmats_before[8]
    assert mats_before['fuel']['Cm240'] == tmats_before[1610]
    assert mats_before['fuel']['Pu239'] == tmats_before[1589]
    # still need to do these ones!!
    assert mats_before['ctrlPois']['Gd155'] ==
    assert mats_before['ctrlPois']['O16'] ==


    # then tdo one for mats_after

    # then remove the entries you added to the file

def test_store_run_init_info()

def test_store_run_step_info()


def test_read_k_eds_delta():
    assert simulation.read_k_eds_delta(7, False) is False


def test_switch_to_next_geometry():
    shutil.copy2(geo_test_input, serpent.input_path + '_test')
    serpent.input_path = serpent.input_path + '_test'
    simulation.switch_to_next_geometry()
    d = serpent.read_depcode_template(serpent.input_path)
    assert d[5].split('/')[-1] == '988.inp"\n'
    os.remove(serpent.input_path)
