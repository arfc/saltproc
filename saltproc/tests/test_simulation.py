from __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent
from saltproc import Simulation
import saltproc.app
import os
import sys
import numpy as np
import tables as tb
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
iter_inputfile = directory + '/test'
main_input = directory + '/test.json'
dot_input = directory + '/test.dot'

serpent = DepcodeSerpent(
    exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
    template_input_file_path=directory + '/template.inp',
    geo_files=[
        '../../examples/406.inp',
        '../../examples/988.inp'])

serpent.iter_inputfile = iter_inputfile
serpent.iter_matfile = directory + '/material'


simulation = Simulation(sim_name='Simulation unit tests',
                        sim_depcode=serpent,
                        core_number=1,
                        node_number=1,
                        db_path=directory + '/test_db.h5')


def test_check_switch_geo_trigger():
    """
    This unit test checks that ``check_switch_geo_trigger`` functions
    consistently with its docstring.
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


def test_store_after_repr():
    """
    This unit test checks that select entries that ``store_after_repr_()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.

    unchecked processes: waste_bypass
                        waste_core_inlet
                        waste_core_outlet
                        waste_heat_exchanger
                        removal_tb_dy
                        feed_pure_gd

    """
    saltproc.app.read_main_input(main_input)

    # read data
    mats = simulation.sim_depcode.read_dep_comp(
        True)
    waste_st, rem_mass = saltproc.app.reprocess_materials(mats)
    m_after_refill = saltproc.app.refill_materials(mats, rem_mass, waste_st)

    fuel_st = m_after_refill['fuel']

    f_feed_leu = fuel_st['feed_leu']
    f_entrain_sep = fuel_st['waste_entrainment_separator']
    f_liq_met = fuel_st['waste_liquid_metal']
    f_nickel_filt = fuel_st['waste_nickel_filter']
    f_sparger = fuel_st['waste_sparger']

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = serpent.iter_inputfile + '.h5'
    simulation.db_path = db_file

    # store data
    simulation.store_mat_data(mats, 0, False)
    simulation.store_after_repr(mats, m_after_refill, 0)

    # read stored data
    try:
        db = tb.open_file(simulation.db_path, mode='r',
                          filters=simulation.compression_params)
    except Exception:
        print('Unable to assign correct value to db.\
              See error stack for more info.')

    tmats = db.root.materials
    tfuel_st = tmats.fuel.in_out_streams

    tf_feed_leu = tfuel_st.feed_leu[0]
    tf_entrain_sep = tfuel_st.waste_entrainment_separator[0]
    tf_liq_met = tfuel_st.waste_liquid_metal[0]
    tf_nickel_filt = tfuel_st.waste_nickel_filter[0]
    tf_sparger = tfuel_st.waste_sparger[0]
    try:
        assert tf_feed_leu[0] == f_feed_leu['Li6']
        assert tf_feed_leu[1] == f_feed_leu['Li7']
        assert tf_feed_leu[2] == f_feed_leu['F19']
        assert tf_feed_leu[3] == f_feed_leu['U235']
        assert tf_feed_leu[4] == f_feed_leu['U238']

        assert tf_entrain_sep[0] == f_entrain_sep['H1']
        assert tf_entrain_sep[1] == f_entrain_sep['H2']
        assert tf_entrain_sep[459] == f_entrain_sep['Kr91']
        assert tf_entrain_sep[461] == f_entrain_sep['Kr93']
        assert tf_entrain_sep[991] == f_entrain_sep['Xe135']
        assert tf_entrain_sep[993] == f_entrain_sep['Xe136']

        assert tf_liq_met[117] == f_liq_met['Ca49']
        assert tf_liq_met[288] == f_liq_met['Cu69']
        assert tf_liq_met[513] == f_liq_met['Sr102']
        assert tf_liq_met[518] == f_liq_met['Y89']
        assert tf_liq_met[1123] == f_liq_met['Pr159']
        assert tf_liq_met[1124] == f_liq_met['Nd142']

        assert tf_nickel_filt[309] == f_nickel_filt['Zn70']
        assert tf_nickel_filt[437] == f_nickel_filt['Br90']
        assert tf_nickel_filt[964] == f_nickel_filt['I134']
        assert tf_nickel_filt[630] == f_nickel_filt['Tc99']

        assert tf_sparger[0] == f_sparger['H1']
        assert tf_sparger[1] == f_sparger['H2']
        assert tf_sparger[459] == f_sparger['Kr91']
        assert tf_sparger[461] == f_sparger['Kr93']
        assert tf_sparger[991] == f_sparger['Xe135']
        assert tf_sparger[993] == f_sparger['Xe136']
    except AssertionError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise AssertionError("incorrect Value")
    except KeyError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise KeyError("incorrect key")
    except BaseException:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        print("something went wrong. See error stack for details")

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
    simulation.db_path = db_path_old


def test_store_mat_data():
    """
    This unit test checks that select entries that ``store_mat_data_()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """
    # read data
    mats_before = simulation.sim_depcode.read_dep_comp(
        False)
    mats_after = simulation.sim_depcode.read_dep_comp(
        True)

    fuel_before = mats_before['fuel']
    pois_before = mats_before['ctrlPois']

    fuel_after = mats_after['fuel']
    pois_after = mats_after['ctrlPois']

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = serpent.iter_inputfile + '.h5'
    simulation.db_path = db_file

    # store data at end
    simulation.store_mat_data(mats_before, 0, False)
    simulation.store_mat_data(mats_after, 0, True)

    # read stored data
    try:
        db = tb.open_file(simulation.db_path, mode='r',
                          filters=simulation.compression_params)
    except Exception:
        print('Unable to assign correct value to db.\
              See error stack for more info.')

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
    try:
        assert tfuel_before[1566] == fuel_before['U235']
        assert tfuel_before[1570] == fuel_before['U238']
        assert tfuel_before[37] == fuel_before['F19']
        assert tfuel_before[8] == fuel_before['Li7']
        assert tfuel_before[1610] == fuel_before['Cm240']
        assert tfuel_before[1589] == fuel_before['Pu239']
        assert tpois_before[1213] == pois_before['Gd155']
        assert tpois_before[32] == pois_before['O16']

        assert tfuel_after[1566] == fuel_after['U235']
        assert tfuel_after[1570] == fuel_after['U238']
        assert tfuel_after[37] == fuel_after['F19']
        assert tfuel_after[8] == fuel_after['Li7']
        assert tfuel_after[1610] == fuel_after['Cm240']
        assert tfuel_after[1589] == fuel_after['Pu239']
        assert tpois_after[1213] == pois_after['Gd155']
        assert tpois_after[32] == pois_after['O16']

        # Check the parameters
        assert tfuel_before_params[0] == fuel_before.mass
        assert tfuel_before_params[1] == fuel_before.density
        assert tfuel_before_params[2] == fuel_before.vol
        assert tfuel_before_params[3] == fuel_before.temp
        assert tfuel_before_params[4] == fuel_before.mass_flowrate
        assert tfuel_before_params[5] == fuel_before.void_frac
        assert tfuel_before_params[6] == fuel_before.burnup

        assert tpois_before_params[0] == pois_before.mass
        assert tpois_before_params[1] == pois_before.density
        assert tpois_before_params[2] == pois_before.vol
        assert tpois_before_params[3] == pois_before.temp
        assert tpois_before_params[4] == pois_before.mass_flowrate
        assert tpois_before_params[5] == pois_before.void_frac
        assert tpois_before_params[6] == pois_before.burnup

        assert tfuel_after_params[0] == fuel_after.mass
        assert tfuel_after_params[1] == fuel_after.density
        assert tfuel_after_params[2] == fuel_after.vol
        assert tfuel_after_params[3] == fuel_after.temp
        assert tfuel_after_params[4] == fuel_after.mass_flowrate
        assert tfuel_after_params[5] == fuel_after.void_frac
        assert tfuel_after_params[6] == fuel_after.burnup

        assert tpois_after_params[0] == pois_after.mass
        assert tpois_after_params[1] == pois_after.density
        assert tpois_after_params[2] == pois_after.vol
        assert tpois_after_params[3] == pois_after.temp
        assert tpois_after_params[4] == pois_after.mass_flowrate
        assert tpois_after_params[5] == pois_after.void_frac
        assert tpois_after_params[6] == pois_after.burnup
    except AssertionError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise AssertionError("incorrect Value")
    except KeyError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise KeyError("incorrect key")
    except BaseException:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        print("something went wrong. See error stack for details")

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
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
    db_file = serpent.iter_inputfile + '.h5'
    simulation.db_path = db_file

    # store data at
    simulation.store_run_init_info()

    # read stored data
    try:
        db = tb.open_file(simulation.db_path, mode='r',
                          filters=simulation.compression_params)
    except Exception:
        db.close()
        print('Unable to assign correct value to db.\
              See error stack for more info.')

    tinit_info = db.root.initial_depcode_siminfo[0]

    try:
        assert tinit_info[0] == simulation.sim_depcode.npop
        assert tinit_info[1] == simulation.sim_depcode.active_cycles
        assert tinit_info[2] == simulation.sim_depcode.inactive_cycles
        assert str(tinit_info[3])[2:-1] == init_info['depcode_name']
        assert str(tinit_info[4])[2:-1] == init_info['depcode_version']
        assert str(tinit_info[5])[2:-1] == init_info['title']
        assert str(tinit_info[6])[2:-1] == init_info['depcode_input_filename']
        assert str(tinit_info[7])[2:-1] == init_info['depcode_working_dir']
        assert str(tinit_info[8])[2:-1] == init_info['xs_data_path']
        assert tinit_info[9] == init_info['OMP_threads']
        assert tinit_info[10] == init_info['MPI_tasks']
        assert tinit_info[11] == init_info['memory_optimization_mode']
        assert tinit_info[12] == init_info['depletion_timestep']
    except AssertionError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise AssertionError("incorrect Value")
    except KeyError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise KeyError("incorrect key")
    except BaseException:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        print("something went wrong. See error stack for details")

        print("")

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
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
    db_file = serpent.iter_inputfile + '.h5'
    simulation.db_path = db_file

    # store data at
    simulation.store_run_step_info()

    # read stored data
    try:
        db = tb.open_file(simulation.db_path, mode='r',
                          filters=simulation.compression_params)
    except Exception:
        print('Unable to assign correct value to db.\
              See error stack for more info.')

    tstep_info = db.root.simulation_parameters[0]
    try:
        assert np.array_equal(tstep_info[0],
                              step_info['beta_eff'].astype('float32'))
        assert np.array_equal(tstep_info[1],
                              step_info['breeding_ratio'].astype('float32'))
        assert tstep_info[2] == simulation.burn_time
        assert np.array_equal(tstep_info[3],
                              step_info['delayed_neutrons_lambda'].
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
    except AssertionError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise AssertionError("incorrect Value")
    except KeyError:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        raise KeyError("incorrect key")
    except BaseException:
        db.close()
        os.remove(db_file)
        simulation.db_path = db_path_old
        print("something went wrong. See error stack for details")

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
    simulation.db_path = db_path_old


def test_read_k_eds_delta():
    assert simulation.read_k_eds_delta(7) is False
