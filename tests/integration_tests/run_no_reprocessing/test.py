"""Run SaltProc without reprocessing"""
import os
import glob
from pathlib import Path

import numpy as np
import pytest

from pyne import serpent
from saltproc import app
from saltproc import SerpentDepcode, Simulation, Reactor


@pytest.fixture
def setup():
    cwd = Path(__file__).parents[0].resolve().as_posix()
    main_input = cwd + '/test_input.json'

    input_path, process_input_file, path_input_file, object_input = \
        app.read_main_input(main_input)

    depcode = app._create_depcode_object(object_input[0])
    sss_file = cwd + '/_test'
    depcode.iter_inputfile = sss_file
    depcode.iter_matfile = cwd + '/_test_mat'

    simulation = app._create_simulation_object(object_input[1], depcode, 1, 1)

    reactor = app._create_reactor_object(object_input[2])

    return cwd, simulation, reactor, sss_file


@pytest.mark.slow
def test_integration_2step_saltproc_no_reproc_heavy(setup):
    cwd, simulation, reactor, sss_file = setup
    runsim_no_reproc(simulation, reactor, 2)
    saltproc_out = sss_file + '_dep.m'

    ref_result = serpent.parse_dep(cwd + '/reference_dep.m', make_mats=False)
    test_result = serpent.parse_dep(saltproc_out, make_mats=False)

    ref_mdens_error = np.loadtxt(cwd + '/reference_error')

    ref_fuel_mdens = ref_result['MAT_fuel_MDENS'][:, -2]
    test_fuel_mdens = test_result['MAT_fuel_MDENS'][:, -1]

    test_mdens_error = np.array(ref_fuel_mdens - test_fuel_mdens)
    np.testing.assert_array_almost_equal(test_mdens_error, ref_mdens_error)
    # Cleaning after testing
    out_file_list = glob.glob(cwd + '/_test*')
    for file in out_file_list:
        try:
            os.remove(file)
        except OSError:
            print("Error while deleting file : ", file)


def runsim_no_reproc(simulation, reactor, nsteps):
    """Run simulation sequence for integration test. No reprocessing
    involved, just re-running depletion code for comparision with model
    output.

    Parameters
    ----------
    simulation : Simulation
        Simulation object
    reactor : Reactor
        Contains information about power load curve and cumulative
        depletion time for the integration test.
    nsteps : int
        Number of depletion time steps in integration test run.

    """

    ######################################################################
    # Start sequence
    for dep_step in range(nsteps):
        print("\nStep #%i has been started" % (dep_step + 1))
        if dep_step == 0:  # First step
            simulation.sim_depcode.write_depcode_input(
                reactor,
                dep_step,
                False)
            simulation.sim_depcode.run_depcode(
                simulation.core_number,
                simulation.node_number)
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dep_step)
            mats = simulation.sim_depcode.read_dep_comp(
                False)
            simulation.store_mat_data(mats, dep_step, False)
        # Finish of First step
        # Main sequence
        else:
            simulation.sim_depcode.run_depcode(
                simulation.core_number,
                simulation.node_number)
        mats = simulation.sim_depcode.read_dep_comp(
            True)
        simulation.store_mat_data(mats, dep_step, False)
        simulation.store_run_step_info()
        simulation.sim_depcode.write_mat_file(
            mats,
            simulation.burn_time)
