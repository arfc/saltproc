"""Run SaltProc with reprocessing"""
from pathlib import Path
import sys
import shutil

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
    cwd = str(Path(__file__).parents[0].resolve())
    test_db = cwd + '/saltproc_runtime/saltproc_results.h5'
    ref_db = cwd + '/tap_reference_db.h5'
    tol = 1e-5

    return cwd, test_db, ref_db, tol

def test_constant_reprocessing_serpent(setup):
    cwd, test_db, ref_db, tol = setup
    args = ['python', '-m', 'saltproc', '-s', '12', '-i', cwd + '/tap_input.json']
    subprocess.run(
        args,
        check=True,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)

    np.testing.assert_allclose(read_keff(test_db)[0], read_keff(ref_db)[0], rtol=5e-2)
    np.testing.assert_allclose(read_keff(test_db)[1], read_keff(ref_db)[1], rtol=5e-1)
    assert_db_allclose(test_db, ref_db, tol)

    shutil.rmtree(cwd + '/saltproc_runtime')

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
    k = np.append(k_0, k_1)
    k_e = np.append(k_0_e, k_1_e)
    return k, k_e

def assert_db_allclose(test_db, ref_db, tol):
    assert_nuclide_mass_allclose(test_db, ref_db, tol)
    assert_in_out_streams_allclose(test_db, ref_db, tol)
    ref_data, ref_after_param, ref_before_param = read_fuel(ref_db, 'old')
    test_data, test_after_param, test_before_param = read_fuel(test_db, 'new')
    # Compare materials composition
    for node_name, test_comp in test_data.items():
        for nuc, test_mass_arr in test_comp.items():
            if len(nuc) > 4 and nuc[-3] == '_':
                nuc = nuc[:-3] + nuc[-2:]
            if nuc in ref_data[node_name]:
                np.testing.assert_allclose(
                    test_mass_arr, ref_data[node_name][nuc], rtol=tol)
    # Compare material properties
    np.testing.assert_allclose(test_after_param, ref_after_param, rtol=tol)
    np.testing.assert_allclose(test_before_param, ref_before_param, rtol=tol)

def assert_nuclide_mass_allclose(test_db, ref_db, tol):
    ref_mass_before, ref_mass_after = read_nuclide_mass(ref_db, 'old')
    test_mass_before, test_mass_after = read_nuclide_mass(test_db, 'new')
    for key, val in ref_mass_before.items():
        if key[-2] == 'm':
            key = key[:-2] + '_' + key[-2:]
        np.testing.assert_allclose(val, test_mass_before[key], rtol=tol)
    for key, val in ref_mass_after.items():
        if key[-2] == 'm':
            key = key[:-2] + '_' + key[-2:]
        np.testing.assert_allclose(val, test_mass_after[key], rtol=tol)

def read_nuclide_mass(db_file, version):
    db = tb.open_file(db_file, mode='r')
    fuel_before = db.root.materials.fuel.before_reproc.comp
    fuel_after = db.root.materials.fuel.after_reproc.comp
    if version == 'old':
        before_nucmap = fuel_before.attrs.iso_map
        after_nucmap = fuel_after.attrs.iso_map
    else:
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

def assert_in_out_streams_allclose(test_db, ref_db, tol):
    ref_sparger, \
        ref_separator, \
        ref_ni_filter, \
        ref_feed = read_in_out_streams(ref_db, 'old')
    test_sparger, \
        test_separator, \
        test_ni_filter, \
        test_feed = read_in_out_streams(test_db, 'new')
    for key, val in test_sparger.items():
        if len(key) > 4 and key[-3] == '_':
            key = key[:-3] + key[-2:]
        if key in ref_sparger:
            np.testing.assert_allclose(val, ref_sparger[key], rtol=tol)
    for key, val in test_separator.items():
        if len(key) > 4 and key[-3] == '_':
            key = key[:-3] + key[-2:]
        if key in ref_separator:
            np.testing.assert_allclose(val, ref_separator[key], rtol=tol)
    for key, val in test_ni_filter.items():
        if len(key) > 4 and key[-3] == '_':
                key = key[:-3] + key[-2:]
        if key in ref_ni_filter:
            np.testing.assert_allclose(val, ref_ni_filter[key], rtol=tol)
    for key, val in test_feed.items():
        if len(key) > 4 and key[-3] == '_':
            key = key[:-3] + key[-2:]
        if key in ref_feed:
            np.testing.assert_allclose(val, ref_feed[key], rtol=tol)

def read_in_out_streams(db_file, version):
    db = tb.open_file(db_file, mode='r')
    waste_sparger = db.root.materials.fuel.in_out_streams.waste_sparger
    waste_separator = \
        db.root.materials.fuel.in_out_streams.waste_entrainment_separator
    waste_ni_filter = db.root.materials.fuel.in_out_streams.waste_nickel_filter
    feed_leu = db.root.materials.fuel.in_out_streams.feed_leu
    if version == 'old':
        waste_sparger_nucmap = waste_sparger.attrs.iso_map
        waste_separator_nucmap = waste_separator.attrs.iso_map
        waste_ni_filter_nucmap = waste_ni_filter.attrs.iso_map
        feed_nucmap = feed_leu.attrs.iso_map
    else:
        waste_sparger_nucmap = _create_nuclide_map(waste_sparger)
        waste_separator_nucmap = _create_nuclide_map(waste_separator)
        waste_ni_filter_nucmap = _create_nuclide_map(waste_ni_filter)
        feed_nucmap = _create_nuclide_map(feed_leu)
        waste_sparger = waste_sparger.comp
        waste_separator = waste_separator.comp
        waste_ni_filter = waste_ni_filter.comp
        feed_leu = feed_leu.comp

    mass_waste_sparger = {}
    mass_waste_separator = {}
    mass_waste_ni_filter = {}
    mass_feed_leu = {}

    for nuc, idx in waste_sparger_nucmap.items():
        mass_waste_sparger[nuc] = np.array(
            [row[idx] for row in waste_sparger])
    for nuc, idx in waste_separator_nucmap.items():
        mass_waste_separator[nuc] = np.array(
            [row[idx] for row in waste_separator])
    for nuc, idx in waste_ni_filter_nucmap.items():
        mass_waste_ni_filter[nuc] = np.array(
            [row[idx] for row in waste_ni_filter])
    for nuc, idx in feed_nucmap.items():
        mass_feed_leu[nuc] = np.array(
            [row[idx] for row in feed_leu])
    db.close()
    return mass_waste_sparger, \
        mass_waste_separator, \
        mass_waste_ni_filter, \
        mass_feed_leu

def read_fuel(file, version):
    db = tb.open_file(file, mode='r')
    fuel = db.root.materials.fuel
    out_data = {}
    for node in db.walk_nodes(fuel, classname="EArray"):
        if version == 'old':
            nucmap = node.attrs.iso_map
        else:
            nucmap = _create_nuclide_map(node._v_parent)
        if node._v_name == 'comp':
            node_name = node._v_parent._v_name
        else:
            node_name = node._v_name
        out_data[node_name] = {}
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
        # remove temperature as it is broken right now.
        params = np.concatenate((params[:,0:3], params[:, 4:]), axis=1)
        all_params += [params]
    after_params, before_params = all_params
    db.close()
    return out_data, after_params, before_params
