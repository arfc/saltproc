from pathlib import Path
import os

import pytest
import numpy as np
import tables as tb

from saltproc.app import reprocess_materials, refill_materials


@pytest.fixture(scope='module')
def db_file(simulation):
    cwd = Path.cwd()
    db_file = (cwd / (simulation.sim_depcode.codename + '_test.h5'))
    return str(db_file.resolve())

def _create_nuclide_map(node):
    nuclides = list(map(bytes.decode, node.nuclide_map.col('nuclide')))
    indices = node.nuclide_map.col('index')
    return dict(zip(nuclides, indices))

def test_store_after_reprocessing(
        simulation,
        proc_test_file,
        path_test_file,
        db_file):
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
    # read data
    mats = simulation.sim_depcode.read_depleted_materials(
        True)
    waste_streams, extracted_mass = reprocess_materials(
        mats, proc_test_file, path_test_file)
    waste_feed_streams = refill_materials(
        mats, extracted_mass, waste_streams, proc_test_file)

    fuel_stream = waste_feed_streams['fuel']

    f_feed_leu = fuel_stream['feed_leu']
    f_entrain_sep = fuel_stream['waste_entrainment_separator']
    f_liq_met = fuel_stream['waste_liquid_metal']
    f_nickel_filt = fuel_stream['waste_nickel_filter']
    f_sparger = fuel_stream['waste_sparger']

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh database
    db_path_old = simulation.db_path
    simulation.db_path = db_file

    # store data
    simulation.store_mat_data(mats, 0, False)
    simulation.store_after_repr(mats, waste_feed_streams, 0)

    # read stored data
    try:
        db = tb.open_file(simulation.db_path, mode='r',
                          filters=simulation.compression_params)
    except Exception:
        print('Unable to assign correct value to db.\
              See error stack for more info.')

    tmats = db.root.materials
    tfuel_stream = tmats.fuel.in_out_streams

    tf_feed_leu = tfuel_stream.feed_leu.comp[0]
    tf_feed_leu_map = _create_nuclide_map(tfuel_stream.feed_leu)

    tf_entrain_sep = tfuel_stream.waste_entrainment_separator.comp[0]
    tf_entrain_sep_map = _create_nuclide_map(tfuel_stream.waste_entrainment_separator)

    tf_liq_met = tfuel_stream.waste_liquid_metal.comp[0]
    tf_liq_met_map = _create_nuclide_map(tfuel_stream.waste_liquid_metal)

    tf_nickel_filt = tfuel_stream.waste_nickel_filter.comp[0]
    tf_nickel_filt_map = _create_nuclide_map(tfuel_stream.waste_nickel_filter)

    tf_sparger = tfuel_stream.waste_sparger.comp[0]
    tf_sparger_map = _create_nuclide_map(tfuel_stream.waste_sparger)

    for nuc in f_feed_leu.get_nuclides():
        np.testing.assert_allclose(tf_feed_leu[tf_feed_leu_map[nuc]],
                                   f_feed_leu.get_mass(nuc))
    for nuc in f_entrain_sep.get_nuclides():
        np.testing.assert_allclose(tf_entrain_sep[tf_entrain_sep_map[nuc]],
                                   f_entrain_sep.get_mass(nuc))
    for nuc in f_liq_met.get_nuclides():
        np.testing.assert_allclose(tf_liq_met[tf_liq_met_map[nuc]],
                                   f_liq_met.get_mass(nuc))
    for nuc in f_nickel_filt.get_nuclides():
        np.testing.assert_allclose(tf_nickel_filt[tf_nickel_filt_map[nuc]],
                                   f_nickel_filt.get_mass(nuc))
    for nuc in f_sparger.get_nuclides():
        np.testing.assert_allclose(tf_sparger[tf_sparger_map[nuc]],
                                   f_sparger.get_mass(nuc))
    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
    simulation.db_path = db_path_old


def test_store_mat_data(simulation):
    """
    This unit test checks that select entries that ``store_mat_data_()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """
    # read data
    mats_before = simulation.sim_depcode.read_depleted_materials(
        False)
    mats_after = simulation.sim_depcode.read_depleted_materials(
        True)

    fuel_before = mats_before['fuel']
    pois_before = mats_before['ctrlPois']

    fuel_after = mats_after['fuel']
    pois_after = mats_after['ctrlPois']

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = simulation.sim_depcode.codename + '_test.h5'
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
    tfuel_before_map = _create_nuclide_map(tmats.fuel.before_reproc)

    tfuel_after = tmats.fuel.after_reproc.comp[0]
    tfuel_after_params = tmats.fuel.after_reproc.parameters[0]
    tfuel_after_map = _create_nuclide_map(tmats.fuel.after_reproc)

    tpois_before = tmats.ctrlPois.before_reproc.comp[0]
    tpois_before_params = tmats.ctrlPois.before_reproc.parameters[0]
    tpois_before_map = _create_nuclide_map(tmats.ctrlPois.before_reproc)

    tpois_after = tmats.ctrlPois.after_reproc.comp[0]
    tpois_after_params = tmats.ctrlPois.after_reproc.parameters[0]
    tpois_after_map = _create_nuclide_map(tmats.ctrlPois.after_reproc)

    # Check the mass fractions
    for nuc in fuel_before.get_nuclides():
        np.testing.assert_allclose(tfuel_before[tfuel_before_map[nuc]],
                            fuel_before.get_mass(nuc))
    for nuc in pois_before.get_nuclides():
        np.testing.assert_allclose(tpois_before[tpois_before_map[nuc]],
                            pois_before.get_mass(nuc))
    for nuc in fuel_after.get_nuclides():
        np.testing.assert_allclose(tfuel_after[tfuel_after_map[nuc]],
                            fuel_after.get_mass(nuc))
    for nuc in pois_after.get_nuclides():
        np.testing.assert_allclose(tpois_after[tpois_after_map[nuc]],
                            pois_after.get_mass(nuc))
    # Check the parameters
    assert tfuel_before_params[0] == fuel_before.mass
    assert tfuel_before_params[1] == fuel_before.density
    assert tfuel_before_params[2] == fuel_before.volume
    #assert tfuel_before_params[3] == fuel_before.temperature
    assert tfuel_before_params[4] == fuel_before.mass_flowrate
    assert tfuel_before_params[5] == fuel_before.void_frac
    assert tfuel_before_params[6] == fuel_before.burnup

    assert tpois_before_params[0] == pois_before.mass
    assert tpois_before_params[1] == pois_before.density
    assert tpois_before_params[2] == pois_before.volume
    #assert tpois_before_params[3] == pois_before.temperature
    assert tpois_before_params[4] == pois_before.mass_flowrate
    assert tpois_before_params[5] == pois_before.void_frac
    assert tpois_before_params[6] == pois_before.burnup

    assert tfuel_after_params[0] == fuel_after.mass
    assert tfuel_after_params[1] == fuel_after.density
    assert tfuel_after_params[2] == fuel_after.volume
    #assert tfuel_after_params[3] == fuel_after.temperature
    assert tfuel_after_params[4] == fuel_after.mass_flowrate
    assert tfuel_after_params[5] == fuel_after.void_frac
    assert tfuel_after_params[6] == fuel_after.burnup

    assert tpois_after_params[0] == pois_after.mass
    assert tpois_after_params[1] == pois_after.density
    assert tpois_after_params[2] == pois_after.volume
    #assert tpois_after_params[3] == pois_after.temperature
    assert tpois_after_params[4] == pois_after.mass_flowrate
    assert tpois_after_params[5] == pois_after.void_frac
    assert tpois_after_params[6] == pois_after.burnup

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
    simulation.db_path = db_path_old


def test_store_run_init_info(simulation):
    """
    This unit test checks that the entries ``store_run_init_info()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """

    # read data
    simulation.sim_depcode.read_step_metadata()

    file = simulation.sim_depcode.template_input_file_path
    file_lines = simulation.sim_depcode.read_plaintext_file(file)
    simulation.sim_depcode.get_neutron_settings(file_lines)
    init_info = simulation.sim_depcode.step_metadata

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = simulation.sim_depcode.codename + '_test.h5'
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
    assert tinit_info[13] == init_info['execution_time']
    assert tinit_info[14] == init_info['memory_usage']

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
    simulation.db_path = db_path_old


def test_store_run_step_info(simulation):
    """
    This unit test checks that the entries ``store_run_step_info()`
    stores in the database match the corresponding entries from the input
    explicity in value and implicitly in type.
    """
    # read data
    simulation.sim_depcode.read_neutronics_parameters()
    step_info = simulation.sim_depcode.neutronics_parameters

    # we want to keep the old path for other sims, but for this
    # test we'll want a fresh db
    db_path_old = simulation.db_path
    db_file = simulation.sim_depcode.codename + '_test.h5'
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
    assert tstep_info[8] == step_info['power_level'].astype('float32')

    # close the file
    db.close()

    # delete test file
    os.remove(db_file)

    # use original db path
    simulation.db_path = db_path_old
