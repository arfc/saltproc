"""Test Materialflow functions"""
def test_get_mass(depcode_serpent):
    mats = depcode_serpent.read_dep_comp(True)
    assert mats['fuel'].get_mass() == 112683343.50000001
    assert mats['ctrlPois'].get_mass() == 65563.2355


def test_scale_matflow(depcode_serpent):
    mats = depcode_serpent.read_dep_comp(True)
    scale_factor = 0.7
    scaled_matflow = mats['fuel'].scale_matflow(scale_factor)
    assert scaled_matflow[922350000] == scale_factor * 3499538.3359278883
    assert scaled_matflow[922380000] == scale_factor * 66580417.24509208
    assert scaled_matflow[90190000] == scale_factor * 37145139.35897285
    assert scaled_matflow[30070000] == scale_factor * 5449107.821098938


def test_copy_pymat_attrs(depcode_serpent):
    mats = depcode_serpent.read_dep_comp(True)
    target_mat = mats['fuel']
    target_mat.copy_pymat_attrs(mats['ctrlPois'])
    assert target_mat.density == 5.873
    assert target_mat.atoms_per_molecule == -1.0
