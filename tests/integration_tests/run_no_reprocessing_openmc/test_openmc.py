"""Run SaltProc without reprocessing"""
from tests.integration_tests import config

import sys
import shutil
from pathlib import Path

import numpy as np
import pytest
import tables as tb
import subprocess

from saltproc import app, Results

@pytest.mark.slow
def test_no_reprocessing_openmc():
    cwd = str(Path(__file__).parents[0].resolve())
    args = ['python', '-m', 'saltproc', '-s', '12', '-i', cwd + '/test_input.json']
    subprocess.run(
        args,
        check=True,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)

    ref_path = cwd + '/ref_saltproc_results.h5'
    test_path = cwd + '/saltproc_runtime/saltproc_results.h5'
    if config['update']:
        shutil.copyfile(test_path, ref_path)

    ref_results = Results(ref_path, load_in_out_streams=False)
    test_results = Results(test_path, load_in_out_streams=False)

    def _get_nucs(res):
        nucs = res.nuclide_idx['fuel']
        mass = []
        for nuc in nucs:
            m = res.get_nuclide_mass('fuel', nuc, -1)
            if np.abs(m) > 1e-15:
                mass += [m]
        return mass
    ref_fuel_mass = _get_nucs(ref_results)
    test_fuel_mass = _get_nucs(test_results)

    test_mass_error = np.array(ref_fuel_mass) - np.array(test_fuel_mass)
    with open(cwd + '/test_error', mode='w') as f:
            test_mass_error.tofile(f, sep='\n')

    if config['update']:
        with open(cwd + '/reference_error', mode='w') as f:
            test_mass_error.tofile(f, sep='\n')
        return

    ref_mass_error = np.loadtxt(cwd + '/reference_error')
    np.testing.assert_array_almost_equal(test_mass_error, ref_mass_error)

    shutil.rmtree(cwd + '/saltproc_runtime')
