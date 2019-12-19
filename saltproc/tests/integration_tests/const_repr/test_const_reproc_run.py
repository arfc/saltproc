from __future__ import absolute_import, division, print_function
from saltproc import Depcode
from saltproc import Simulation
from saltproc import app
import os
import sys
import numpy as np
import pytest
import tables as tb

path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))

# global class object
directory = os.path.dirname(path)

sss_file = directory+'/int_test'
iter_matfile = directory+'/int_test_mat'

db_exp_file = directory+'/2step_non_ideal.h5'
db_file = directory+'/../../../data/db_saltproc.h5'

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
# @pytest.mark.skip
def read_keff_h5(file):
    db = tb.open_file(file, mode='r')
    sim_param = db.root.simulation_parameters
    init_param = db.root.initial_depcode_siminfo
    # Keff at t=0 depletion step
    k_0 = np.array([x['keff_bds'][0] for x in sim_param.iterrows()])
    k_0_e = np.array([x['keff_bds'][1] for x in sim_param.iterrows()])
    # Keff at t=end depletion step
    k_1 = np.array([x['keff_eds'][0] for x in sim_param.iterrows()])
    k_1_e = np.array([x['keff_eds'][1] for x in sim_param.iterrows()])
    depstep = [x['depletion_timestep'] for x in init_param.iterrows()][0]
    db.close()
    return k_0, k_1, k_0_e, k_1_e, depstep


def read_iso_m_h5(db_file):
    db = tb.open_file(db_file, mode='r')
    fuel_before = db.root.materials.fuel.before_reproc.comp
    fuel_after = db.root.materials.fuel.after_reproc.comp
    isomap = fuel_before.attrs.iso_map

    mass_b = {}
    mass_a = {}

    for iso in isomap:
        mass_b[iso] = np.array([row[isomap[iso]] for row in fuel_before])
        mass_a[iso] = np.array([row1[isomap[iso]] for row1 in fuel_after])
    db.close()
    return mass_b, mass_a


def test_integration_2step_constant_ideal_removal_heavy():
    app.run()
    np.testing.assert_equal(read_iso_m_h5(db_file), read_iso_m_h5(db_exp_file))

# def test_integration_3step_saltproc_no_reproc_heavy():
#    simulation.runsim_constant_reproc()
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
