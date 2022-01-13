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
    template_path=directory +
    '/saltproc_9d.inp',
    input_path=sss_file,
    iter_matfile=iter_matfile,
    geo_file=[
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
                        db_path=db_file,
                        iter_matfile=iter_matfile)

tap = Reactor(volume=1.0,
              power_levels=[1.250E+09],
              depl_hist=[3])


@pytest.mark.slow
# @pytest.mark.skip
def test_integration_3step_saltproc_no_reproc_heavy():
    simulation.runsim_no_reproc(tap, 2)
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
