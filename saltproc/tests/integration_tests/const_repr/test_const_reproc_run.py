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

db_exp_file = directory+'/2step_non_ideal_2.h5'
db_file = directory+'/../../../data/db_saltproc.h5'
tol = 1e-6

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


def read_keff_h5(file):
    db = tb.open_file(file, mode='r')
    sim_param = db.root.simulation_parameters
    # Keff at t=0 depletion step
    k_0 = np.array([x['keff_bds'][0] for x in sim_param.iterrows()])
    k_0_e = np.array([x['keff_bds'][1] for x in sim_param.iterrows()])
    # Keff at t=end depletion step
    k_1 = np.array([x['keff_eds'][0] for x in sim_param.iterrows()])
    k_1_e = np.array([x['keff_eds'][1] for x in sim_param.iterrows()])
    db.close()
    return k_0, k_1, k_0_e, k_1_e


def read_h5(file):
    db = tb.open_file(file, mode='r')
    fuel = db.root.materials.fuel
    out_data = {}
    for node in db.walk_nodes(fuel, classname="EArray"):
        isomap = node.attrs.iso_map
        out_data[node._v_name] = {}
        # print(node)
        for iso in isomap:
            out_data[node._v_name][iso] = \
                np.array([row[isomap[iso]] for row in node])
    db.close()
    return out_data


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


def read_inout_h5(db_file):
    db = tb.open_file(db_file, mode='r')
    waste_sprg = db.root.materials.fuel.in_out_streams.waste_sparger
    waste_s = db.root.materials.fuel.in_out_streams.waste_entrainment_separator
    waste_ni = db.root.materials.fuel.in_out_streams.waste_nickel_filter
    feed_leu = db.root.materials.fuel.in_out_streams.feed_leu
    isomap = waste_ni.attrs.iso_map
    isomap_f = feed_leu.attrs.iso_map
    mass_w_sprg = {}
    mass_w_s = {}
    mass_w_ni = {}
    mass_feed_leu = {}

    for iso in isomap:
        mass_w_sprg[iso] = np.array([row[isomap[iso]] for row in waste_sprg])
        mass_w_s[iso] = np.array([row[isomap[iso]] for row in waste_s])
        mass_w_ni[iso] = np.array([row[isomap[iso]] for row in waste_ni])
    for iso in isomap_f:
        mass_feed_leu[iso] = np.array([row[isomap_f[iso]] for row in feed_leu])
    db.close()
    return mass_w_sprg, mass_w_s, mass_w_ni, mass_feed_leu


def assert_waste_check_eq_h5(db, dbe):
    sprg_e, sep_e, ni_e, feed_e = read_inout_h5(dbe)
    sprg, sep, ni, feed = read_inout_h5(db)
    for key, val in sprg_e.items():
        np.testing.assert_almost_equal(val, sprg[key], decimal=tol)
    for key, val in sep_e.items():
        np.testing.assert_almost_equal(val, sep[key], decimal=tol)
    for key, val in ni_e.items():
        np.testing.assert_almost_equal(val, ni[key], decimal=tol)
    for key, val in feed_e.items():
        np.testing.assert_almost_equal(val, feed[key], decimal=tol)


def assert_iso_m_check_eq_h5(db, dbe):
    mass_b_e, mass_a_e = read_iso_m_h5(dbe)
    mass_b, mass_a = read_iso_m_h5(db)
    for key, val in mass_b_e.items():
        np.testing.assert_almost_equal(val, mass_b[key], decimal=tol)
    for key, val in mass_a_e.items():
        np.testing.assert_almost_equal(val, mass_a[key], decimal=tol)


def assert_h5_almost_equal(db, dbe):
    data_exp = read_h5(dbe)
    data = read_h5(db)
    for node_nm, node in data_exp.items():
        for iso, mass_arr in node.items():
            np.testing.assert_allclose(mass_arr, data[node_nm][iso], rtol=tol)


@pytest.mark.slow
# @pytest.mark.skip
def test_integration_2step_constant_ideal_removal_heavy():
    app.run()
    np.testing.assert_equal(read_keff_h5(db_file), read_keff_h5(db_exp_file))
    assert_h5_almost_equal(db_file, db_exp_file)
