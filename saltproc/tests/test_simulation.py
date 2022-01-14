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

def test_check_switch_geo_trigger():
    """
    This unit test checks that ``check_switch_geo_trigger`` functions
    consistent with its docstring.
    """

    switch_times = [1.0, 3, -31, 86.23333, 1e-16, 2e-18, "two o clock"]
    assert simulation.check_switch_geo_trigger(1.0, switch_times) is True
    assert simulation.check_switch_geo_trigger(3, switch_times) is True
    assert simulation.check_switch_geo_trigger(-32, switch_times) is False
    assert simulation.check_switch_geo_trigger(86.233, switch_times) is False
    assert simulation.check_switch_geo_trigger(1e-16, switch_times) is True
    assert simulation.check_switch_geo_trigger(5e-18, switch_times) is False
    assert simulation.check_switch_geo_trigger("three o clock",
                                               switch_times) is False
    assert simulation.check_switch_geo_trigger("two o clock",
                                               switch_times) is True

#def test_store_after_repr():

def test_store_mat_data():
    """
    This unit test checks that select entries that ``store_mat_data_()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """
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
    assert tfuel_before[1566] == mats_before['fuel']['U235']
    assert tfuel_before[1570] == mats_before['fuel']['U238']
    assert tfuel_before[37] == mats_before['fuel']['F19']
    assert tfuel_before[8] == mats_before['fuel']['Li7']
    assert tfuel_before[1610] == mats_before['fuel']['Cm240']
    assert tfuel_before[1589] == mats_before['fuel']['Pu239']
    assert tpois_before[1213] == mats_before['ctrlPois']['Gd155']
    assert tpois_before[32] == mats_before['ctrlPois']['O16']

    assert tfuel_after[1566] == mats_after['fuel']['U235']
    assert tfuel_after[1570] == mats_after['fuel']['U238']
    assert tfuel_after[37] == mats_after['fuel']['F19']
    assert tfuel_after[8] == mats_after['fuel']['Li7']
    assert tfuel_after[1610] == mats_after['fuel']['Cm240']
    assert tfuel_after[1589] == mats_after['fuel']['Pu239']
    assert tpois_after[1213] == mats_after['ctrlPois']['Gd155']
    assert tpois_after[32] == mats_after['ctrlPois']['O16']

    # Check the parameters
    assert tfuel_before_params[0] == mats_before['fuel'].mass
    assert tfuel_before_params[1] == mats_before['fuel'].density
    assert tfuel_before_params[2] == mats_before['fuel'].vol
    assert tfuel_before_params[3] == mats_before['fuel'].temp
    assert tfuel_before_params[4] == mats_before['fuel'].mass_flowrate
    assert tfuel_before_params[5] == mats_before['fuel'].void_frac
    assert tfuel_before_params[6] == mats_before['fuel'].burnup

    assert tpois_before_params[0] == mats_before['ctrlPois'].mass
    assert tpois_before_params[1] == mats_before['ctrlPois'].density
    assert tpois_before_params[2] == mats_before['ctrlPois'].vol
    assert tpois_before_params[3] == mats_before['ctrlPois'].temp
    assert tpois_before_params[4] == mats_before['ctrlPois'].mass_flowrate
    assert tpois_before_params[5] == mats_before['ctrlPois'].void_frac
    assert tpois_before_params[6] == mats_before['ctrlPois'].burnup

    assert tfuel_after_params[0] == mats_after['fuel'].mass
    assert tfuel_after_params[1] == mats_after['fuel'].density
    assert tfuel_after_params[2] == mats_after['fuel'].vol
    assert tfuel_after_params[3] == mats_after['fuel'].temp
    assert tfuel_after_params[4] == mats_after['fuel'].mass_flowrate
    assert tfuel_after_params[5] == mats_after['fuel'].void_frac
    assert tfuel_after_params[6] == mats_after['fuel'].burnup

    assert tpois_after_params[0] == mats_after['ctrlPois'].mass
    assert tpois_after_params[1] == mats_after['ctrlPois'].density
    assert tpois_after_params[2] == mats_after['ctrlPois'].vol
    assert tpois_after_params[3] == mats_after['ctrlPois'].temp
    assert tpois_after_params[4] == mats_after['ctrlPois'].mass_flowrate
    assert tpois_after_params[5] == mats_after['ctrlPois'].void_frac
    assert tpois_after_params[6] == mats_after['ctrlPois'].burnup

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    #use original db path
    simulation.db_path = db_path_old

def test_store_run_init_info():
    """
    This unit test checks that the entries ``store_run_init_info()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """

    # read data
    simulation.sim_depcode.read_depcode_info()
    init_info = simulation.sim_depcode.sim_info

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = serpent.input_path + '.h5'
    simulation.db_path = db_file

    # store data at
    simulation.store_run_init_info()

    # read stored data
    db = tb.open_file(simulation.db_path, mode='r',
                      filters=simulation.compression_params)

    tinit_info = db.root.initial_depcode_siminfo[0]

    assert tinit_info[0] == simulation.sim_depcode.npop
    assert tinit_info[1] == simulation.sim_depcode.active_cycles
    assert tinit_info[2] == simulation.sim_depcode.inactive_cycles
    assert str(tinit_info[3])[2:-1] == init_info['serpent_version']
    assert str(tinit_info[4])[2:-1] == init_info['title']
    assert str(tinit_info[5])[2:-1] == init_info['serpent_input_filename']
    assert str(tinit_info[6])[2:-1] == init_info['serpent_working_dir']
    assert str(tinit_info[7])[2:-1] == init_info['xs_data_path']
    assert tinit_info[8] == init_info['OMP_threads']
    assert tinit_info[9] == init_info['MPI_tasks']
    assert tinit_info[10] == init_info['memory_optimization_mode']
    assert tinit_info[11] == init_info['depletion_timestep']

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    #use original db path
    simulation.db_path = db_path_old

def test_store_run_step_info():
    """
    This unit test checks that the entries ``store_run_step_info()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """
    # read data
    simulation.sim_depcode.read_depcode_step_param()
    step_info = simulation.sim_depcode.param

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = serpent.input_path + '.h5'
    simulation.db_path = db_file

    # store data at
    simulation.store_run_step_info()

    # read stored data
    db = tb.open_file(simulation.db_path, mode='r',
                      filters=simulation.compression_params)

    tstep_info = db.root.simulation_parameters[0]

    assert np.array_equal(tstep_info[0],
                          step_info['beta_eff'].astype('float32'))
    assert np.array_equal(tstep_info[1],
                          step_info['breeding_ratio'].astype('float32'))
    assert tstep_info[2] == simulation.burn_time
    assert np.array_equal(tstep_info[3],
                          step_info['delayed_neutrons_lambda'].\
                          astype('float32'))
    assert tstep_info[4] == step_info['fission_mass_bds'].astype('float32')
    assert tstep_info[5] == step_info['fission_mass_eds'].astype('float32')
    assert np.array_equal(tstep_info[6],
                          step_info['keff_bds'].astype('float32'))
    assert np.array_equal(tstep_info[7],
                          step_info['keff_eds'].astype('float32'))
    assert tstep_info[8] == step_info['memory_usage'].astype('float32')
    assert tstep_info[9] == step_info['power_level'].astype('float32')
    assert tstep_info[10] == step_info['execution_time'].astype('float32')

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    #use original db path
    simulation.db_path = db_path_old



def test_read_k_eds_delta():
    assert simulation.read_k_eds_delta(7, False) is False


def test_switch_to_next_geometry():
    shutil.copy2(geo_test_input, serpent.input_path + '_test')
    serpent.input_path = serpent.input_path + '_test'
    simulation.switch_to_next_geometry()
    d = serpent.read_depcode_template(serpent.input_path)
    assert d[5].split('/')[-1] == '988.inp"\n'
    os.remove(serpent.input_path)
