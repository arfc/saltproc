from __future__ import absolute_import, division, print_function
from saltproc import Depcode
from saltproc import Simulation
import os
import sys
import numpy as np
import pytest

path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))

# global class object
directory = os.path.dirname(path)

sss_file = directory+'/int_test'
iter_matfile = directory+'/int_test_mat'
db_file = directory+'/db_test.h5'

serpent = Depcode(codename='SERPENT',
                  exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
                  template_fname=directory+'/tap_template.inp',
                  input_fname=sss_file,
                  output_fname='NONE',
                  iter_matfile=iter_matfile,
                  geo_file=[2,
                            os.path.join(directory, '../../test_geo.inp')],
                  npop=100,
                  active_cycles=20,
                  inactive_cycles=5)
simulation = Simulation(sim_name='Integration test with const extraction rate',
                        sim_depcode=serpent,
                        core_number=1,
                        node_number=1,
                        h5_file=db_file,
                        compression=None,
                        iter_matfile=iter_matfile,
                        timesteps=2)


@pytest.mark.slow
@pytest.mark.skip
def test_integration_2step_constant_ideal_removal_heavy():
    for dts in range(simulation.timesteps):
        print ("\n\n\nStep #%i has been started" % (dts+1))
        if dts == 0:  # First step
            serpent.write_depcode_input(serpent.template_fname,
                                        serpent.input_fname)
            serpent.run_depcode(simulation.core_number, simulation.node_number)
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dts
            mats = serpent.read_dep_comp(serpent.input_fname, 0)  # 0)
            simulation.store_mat_data(mats, dts-1, 'before_reproc')
        # Finish of First step
        # Main sequence
        else:
            serpent.run_depcode(simulation.core_number, simulation.node_number)
        mats = serpent.read_dep_comp(serpent.input_fname, 1)
        simulation.store_mat_data(mats, dts, 'before_reproc')
        simulation.store_run_step_info()
        # Reprocessing here
        waste_st, rem_mass = reprocessing(mats)
        refill(mats, rem_mass, waste_st)
        # Store in DB after reprocessing and refill (right before next depl)
        simulation.store_after_repr(mats, waste_st, dts)
        serpent.write_mat_file(mats, iter_matfile, dts)
        del mats, waste_st, rem_mass
        gc.collect()

#def test_integration_3step_saltproc_no_reproc_heavy():
#    simulation.runsim_no_reproc()
#    saltproc_out = sss_file + '_dep.m'
#    dep_ser = serpent.parse_dep(directory+'/serpent_9d_dep.m', make_mats=False)
#    dep_sp = serpent.parse_dep(saltproc_out, make_mats=False)
#    err_expec = np.loadtxt(directory+'/sss_vs_sp_no_reproc_error')
#    fuel_mdens_serpent_eoc = dep_ser['MAT_fuel_MDENS'][:, -2]
#    fuel_mdens_sp_eoc = dep_sp['MAT_fuel_MDENS'][:, -1]
#    err_res = np.array(fuel_mdens_serpent_eoc-fuel_mdens_sp_eoc)
    # print(err_res.shape)
    # print(err_expec.shape)
    # print(err_res)
#    np.testing.assert_array_equal(err_res, err_expec)
