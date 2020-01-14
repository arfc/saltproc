#  __future__ import absolute_import, division, print_function
from saltproc import Depcode
from saltproc import Simulation
from pyne import serpent
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

depcode = Depcode(codename='SERPENT',
                  exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
                  template_fname=directory+'/saltproc_9d.inp',
                  input_fname=sss_file,
                  output_fname='NONE',
                  iter_matfile=iter_matfile,
                  geo_file=[os.path.join(directory, '../../test_geo.inp')],
                  npop=100,
                  active_cycles=20,
                  inactive_cycles=5)
simulation = Simulation(sim_name='Integration test',
                        sim_depcode=depcode,
                        core_number=1,
                        node_number=1,
                        h5_file=db_file,
                        compression=None,
                        iter_matfile=iter_matfile,
                        timesteps=2)


@pytest.mark.slow
@pytest.mark.skip
def test_integration_3step_saltproc_no_reproc_heavy():
    simulation.runsim_no_reproc()
    saltproc_out = sss_file + '_dep.m'
    dep_ser = serpent.parse_dep(directory+'/serpent_9d_dep.m', make_mats=False)
    dep_sp = serpent.parse_dep(saltproc_out, make_mats=False)
    err_expec = np.loadtxt(directory+'/sss_vs_sp_no_reproc_error')
    fuel_mdens_serpent_eoc = dep_ser['MAT_fuel_MDENS'][:, -2]
    fuel_mdens_sp_eoc = dep_sp['MAT_fuel_MDENS'][:, -1]
    err_res = np.array(fuel_mdens_serpent_eoc-fuel_mdens_sp_eoc)
    # print(err_res.shape)
    # print(err_expec.shape)
    # print(err_res)
    np.testing.assert_array_equal(err_res, err_expec)
