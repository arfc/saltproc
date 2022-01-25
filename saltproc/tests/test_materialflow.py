from __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent
import os
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
# global class object
directory = os.path.dirname(path)
iter_input_file = directory + '/test'

serpent = DepcodeSerpent(
    exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
    template_path=directory +
    '/template.inp',
    iter_input_file=iter_input_file,
    iter_matfile=directory +
    '/material',
    geo_files=None)


def test_get_mass():
    mats = serpent.read_dep_comp(input_file, True)
    assert mats['fuel'].get_mass() == 112683343.50000001
    assert mats['fuel']['U235'] == 3499538.3359278883
    assert mats['fuel']['U238'] == 66580417.24509208
    assert mats['fuel']['F19'] == 37145139.35897285
    assert mats['fuel']['Li7'] == 5449107.821098938
    assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    assert mats['fuel']['Pu239'] == 1231.3628804629795
    assert mats['ctrlPois'].get_mass() == 65563.2355
    assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    assert mats['ctrlPois']['O16'] == 15350.701473655872


def test_scale_matflow():
    mats = serpent.read_dep_comp(input_file, True)
    scale_factor = 0.7
    scaled_matflow = mats['fuel'].scale_matflow(scale_factor)
    assert scaled_matflow[922350000] == scale_factor * 3499538.3359278883
    assert scaled_matflow[922380000] == scale_factor * 66580417.24509208
    assert scaled_matflow[90190000] == scale_factor * 37145139.35897285
    assert scaled_matflow[30070000] == scale_factor * 5449107.821098938


def test_copy_pymat_attrs():
    mats = serpent.read_dep_comp(input_file, True)
    target_mat = mats['fuel']
    target_mat.copy_pymat_attrs(mats['ctrlPois'])
    assert target_mat.density == 5.873
    assert target_mat.atoms_per_molecule == -1.0
