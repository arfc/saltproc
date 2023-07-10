"""Run SaltProc without reprocessing"""
from pathlib import Path
import sys
import shutil

import numpy as np
import pytest
import subprocess

import serpentTools
from saltproc import app

@pytest.mark.slow
def test_integration_2step_saltproc_no_reproc_heavy():
    cwd = str(Path(__file__).parents[0].resolve())
    args = ['python', '-m', 'saltproc', '-s', '12', '-i', cwd + '/test_input.json']
    subprocess.run(
        args,
        check=True,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)

    test_path = cwd + '/saltproc_runtime/step_1_data/runtime_input.serpent_dep.m'
    ref_path = cwd + '/reference_dep.m'

    ref_result = serpentTools.read(ref_path)
    test_result = serpentTools.read(test_path)


    ref_fuel_mdens = ref_result.materials['fuel'].mdens[:, -2]
    test_fuel_mdens = test_result.materials['fuel'].mdens[:, -1]

    test_mdens_error = np.array(ref_fuel_mdens - test_fuel_mdens)

    ref_mdens_error = np.loadtxt(cwd + '/reference_error')

    np.testing.assert_array_almost_equal(test_mdens_error, ref_mdens_error)

    shutil.rmtree(cwd + '/saltproc_runtime')
