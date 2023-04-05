"""Test Materialflow functions"""


def test_get_mass(serpent_depcode):
    mats = serpent_depcode.read_depleted_materials(True)
    assert mats['fuel'].get_mass() == 112683343.50000001
    assert mats['ctrlPois'].get_mass() == 65563.2355


def test_scale_matflow(serpent_depcode):
    mats = serpent_depcode.read_depleted_materials(True)
    scale_factor = 0.7
    scaled_matflow = mats['fuel'].scale_matflow(scale_factor)
    assert scaled_matflow['U235'] == scale_factor * mats['fuel'].get_mass('U235')
    assert scaled_matflow['U238'] == scale_factor * mats['fuel'].get_mass('U238')
    assert scaled_matflow['F19'] == scale_factor * mats['fuel'].get_mass('F19')
    assert scaled_matflow['Li7'] == scale_factor * mats['fuel'].get_mass('Li7')

