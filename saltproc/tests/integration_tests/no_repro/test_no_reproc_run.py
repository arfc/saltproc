#  __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent
from saltproc import Simulation
from saltproc import Reactor
from pyne import serpent
import os
import glob
import sys
import numpy as np
import pytest

path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))

# global class object
directory = os.path.dirname(path)

sss_file = directory + '/int_test'
iter_matfile = directory + '/int_test_mat'
db_file = directory + '/db_test.h5'

depcode = DepcodeSerpent(
    exec_path='sss2',
    input_template_path=directory +
    '/saltproc_9d.inp',
    iter_input_file=sss_file,
    iter_matfile=iter_matfile,
    geo_files=[
        os.path.join(
            directory,
            '../../test_geo.inp')],
    npop=100,
    active_cycles=20,
    inactive_cycles=5)
simulation = Simulation(sim_name='Integration test',
                        sim_depcode=depcode,
                        core_number=1,
                        node_number=1,
                        db_path=db_file)

tap = Reactor(volume=1.0,
              power_levels=[1.250E+09],
              depl_hist=[3])

def runsim_no_reproc(simulation, reactor, nsteps):
        """Run simulation sequence for integration test. No reprocessing
        involved, just re-running depletion code for comparision with model
        output.

        Parameters
        ----------
        reactor : `Reactor`
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


@pytest.mark.slow
# @pytest.mark.skip
def test_integration_3step_saltproc_no_reproc_heavy():
    runsim_no_reproc(simulation, tap, 2)
    saltproc_out = sss_file + '_dep.m'
    dep_ser = serpent.parse_dep(
        directory + '/serpent_9d_dep.m',
        make_mats=False)
    dep_sp = serpent.parse_dep(saltproc_out, make_mats=False)
    err_expec = np.loadtxt(directory + '/sss_vs_sp_no_reproc_error')
    fuel_mdens_serpent_eoc = dep_ser['MAT_fuel_MDENS'][:, -2]
    fuel_mdens_sp_eoc = dep_sp['MAT_fuel_MDENS'][:, -1]
    err_res = np.array(fuel_mdens_serpent_eoc - fuel_mdens_sp_eoc)
    np.testing.assert_array_equal(err_res, err_expec)
    # Cleaning after testing
    out_file_list = glob.glob(directory + '/int_test*')
    for file in out_file_list:
        try:
            os.remove(file)
        except OSError:
            print("Error while deleting file : ", file)
