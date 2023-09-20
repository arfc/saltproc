"""Run SaltProc with reprocessing"""
from tests.integration_tests import config

import os
import shutil
from pathlib import Path
import sys

import numpy as np
import pytest

import tables as tb
import subprocess

def _create_nuclide_map(node):
    nuclides = list(map(bytes.decode, node.nuclide_map.col('nuclide')))
    indices = node.nuclide_map.col('index')
    return dict(zip(nuclides, indices))


@pytest.fixture
def setup(scope='module'):
    cwd = Path(__file__).parents[0].resolve()
    os.chdir(cwd)
    test_db = cwd / 'saltproc_runtime/saltproc_results.h5'
    ref_db = cwd / 'pincell_reference_results.h5'
    atol = 3e-3
    rtol = 5e-2

    return cwd, test_db, ref_db, atol, rtol

def test_constant_reprocesing_openmc(setup):
    cwd, test_db, ref_db, atol, rtol = setup
    args = ['python', '-m', 'saltproc', '-i', str(cwd / 'pincell_input.json')]
    subprocess.run(
        args,
        check=True,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
    if config['update']:
        shutil.copyfile(test_db, ref_db)
        return
    np.testing.assert_allclose(read_keff(test_db), read_keff(ref_db), atol=atol)
    assert_db_allclose(test_db, ref_db, atol, rtol)

    shutil.rmtree(cwd / 'saltproc_runtime')

def read_keff(file):
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

def assert_db_allclose(test_db, ref_db, atol, rtol):
    assert_nuclide_mass_allclose(test_db, ref_db, atol, rtol)
    assert_in_out_streams_allclose(test_db, ref_db, atol, rtol)
    ref_data, ref_after_param, ref_before_param = read_fuel(ref_db)
    test_data, test_after_param, test_before_param = read_fuel(test_db)
    for node_name, test_comp in test_data.items():
        for nuc, test_mass_arr in test_comp.items():
            np.testing.assert_allclose(
                test_mass_arr, ref_data[node_name][nuc], rtol=rtol)
    # Compare material properties
    np.testing.assert_allclose(test_after_param, ref_after_param, rtol=rtol)
    np.testing.assert_allclose(test_before_param, ref_before_param, rtol=rtol)


def assert_nuclide_mass_allclose(test_db, ref_db, atol, rtol):
    ref_mass_before, ref_mass_after = read_nuclide_mass(ref_db)
    test_mass_before, test_mass_after = read_nuclide_mass(test_db)
    for key, val in ref_mass_before.items():
        np.testing.assert_allclose(val, test_mass_before[key], atol=atol, rtol=rtol)
    for key, val in ref_mass_after.items():
        np.testing.assert_allclose(val, test_mass_after[key], atol=atol, rtol=rtol)

def read_nuclide_mass(db_file):
    db = tb.open_file(db_file, mode='r')
    fuel_before = db.root.materials.fuel.before_reproc.comp
    fuel_after = db.root.materials.fuel.after_reproc.comp

    before_nucmap = _create_nuclide_map(db.root.materials.fuel.before_reproc)
    after_nucmap = _create_nuclide_map(db.root.materials.fuel.after_reproc)

    mass_before = {}
    mass_after = {}

    for nuc, idx in before_nucmap.items():
        mass_before[nuc] = np.array([row[idx] for row in fuel_before])
    for nuc, idx in after_nucmap.items():
        mass_after[nuc] = np.array([row1[idx] for row1 in fuel_after])
    db.close()
    return mass_before, mass_after

def assert_in_out_streams_allclose(test_db, ref_db, atol, rtol):
    ref_test_separator, \
        ref_feed = read_in_out_streams(ref_db)
    test_separator, \
        test_feed = read_in_out_streams(test_db)
    for key, val in ref_test_separator.items():
        np.testing.assert_allclose(val, test_separator[key], atol=atol, rtol=rtol)
    for key, val in ref_feed.items():
        np.testing.assert_allclose(val, test_feed[key], atol=atol, rtol=rtol)

def read_in_out_streams(db_file):
    db = tb.open_file(db_file, mode='r')
    waste_separator = \
        db.root.materials.fuel.in_out_streams.waste_entrainment_separator
    feed_leu = db.root.materials.fuel.in_out_streams.feed_leu

    waste_separator_nucmap = _create_nuclide_map(waste_separator)
    feed_nucmap = _create_nuclide_map(feed_leu)
    waste_separator = waste_separator.comp
    feed_leu = feed_leu.comp

    mass_waste_separator = {}
    mass_feed_leu = {}

    for nuc, idx in waste_separator_nucmap.items():
        mass_waste_separator[nuc] = np.array(
            [row[idx] for row in waste_separator])
    for nuc, idx in feed_nucmap.items():
        mass_feed_leu[nuc] = np.array(
            [row[idx] for row in feed_leu])
    db.close()
    return mass_waste_separator, \
        mass_feed_leu

def read_fuel(file):
    db = tb.open_file(file, mode='r')
    fuel = db.root.materials.fuel
    out_data = {}
    for node in db.walk_nodes(fuel, classname="EArray"):
        nucmap = _create_nuclide_map(node._v_parent)
        if node._v_name == 'comp':
            node_name = node._v_parent._v_name
        else:
            node_name = node._v_name
        out_data[node_name] = {}
        # print(node)
        for nuc, idx in nucmap.items():
            out_data[node_name][nuc] = \
                np.array([row[idx] for row in node])
    # Read table with material parameters (density, temperature, mass)
    tmp_after = fuel.after_reproc.parameters.read()
    tmp_before = fuel.before_reproc.parameters.read()
    all_params = []
    for tmp in (tmp_after, tmp_before):
        # Convert structured array to simple array
        params = tmp.view(np.float64).reshape(tmp.shape + (-1,))
        all_params += [params]
    after_params, before_params = all_params
    db.close()
    return out_data, after_params, before_params
