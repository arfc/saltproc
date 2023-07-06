"""Run SaltProc without reprocessing"""
import sys
import shutil
from pathlib import Path

import numpy as np
import pytest
import tables as tb
import subprocess

from openmc.deplete import Results
from saltproc import app

@pytest.mark.slow
def test_integration_2step_saltproc_no_reproc_heavy():
    cwd = str(Path(__file__).parents[0].resolve())
    args = ['python', '-m', 'saltproc', '-s', '12', '-i', cwd + '/test_input.json']
    subprocess.run(
        args,
        check=True,
        cwd=cwd,
        stdout=sys.stdout,
        stderr=subprocess.STDOUT)

    ref_results = tb.File('ref_saltproc_results.h5')
    test_results = tb.File('saltproc_runtime/saltproc_results.h5')

    ref_mdens_error = np.loadtxt('reference_error')

    ref_fuel_mdens = ref_results.root.materials.fuel.before_reproc.comp[-1]
    test_fuel_mdens = test_results.root.materials.fuel.before_reproc.comp[-1]

    test_mdens_error = np.array(ref_fuel_mdens) - np.array(test_fuel_mdens)
    np.testing.assert_array_almost_equal(test_mdens_error, ref_mdens_error)

    shutil.rmtree('saltproc_runtime')
