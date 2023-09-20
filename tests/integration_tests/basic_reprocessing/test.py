"""Test basic reprocessing functionality"""
import pytest
import numpy as np
from saltproc.app import reprocess_materials, refill_materials


def test_reprocessing_and_refill(
        serpent_depcode,
        proc_test_file,
        path_test_file):
    mats = serpent_depcode.read_depleted_materials(True)
    waste_streams, extracted_mass = reprocess_materials(mats,
                                                        proc_test_file,
                                                        path_test_file)
    np.testing.assert_allclose(extracted_mass['fuel'], 1401.0846504569054, rtol=1e-6)
    np.testing.assert_allclose(extracted_mass['ctrlPois'], 0.0, rtol=1e-6)
    np.testing.assert_allclose(
        waste_streams['fuel']['waste_sparger'].get_mass('Xe135'),
        11.878661583083327, rtol=1e-6)
    np.testing.assert_allclose(
        waste_streams['fuel']['waste_nickel_filter'].get_mass('I135'),
        0.90990472940444, rtol=1e-6)
    np.testing.assert_allclose(
        waste_streams['fuel']['waste_liquid_metal'].get_mass('Sr90'),
        0.7486923392931839, rtol=1e-6)

    waste_feed_streams = refill_materials(
        mats, extracted_mass, waste_streams, proc_test_file)
    np.testing.assert_allclose(
        waste_feed_streams['fuel']['feed_leu'].get_mass('U235'),
        43.573521906078334, rtol=1e-6)
    np.testing.assert_allclose(
        waste_feed_streams['fuel']['feed_leu'].get_mass('U238'),
        827.8969156550545, rtol=1e-6)
    np.testing.assert_allclose(
        waste_feed_streams['fuel']['feed_leu'].get_mass('F19'),
        461.8575149906222, rtol=1e-6)
    np.testing.assert_allclose(
        waste_feed_streams['fuel']['feed_leu'].get_mass('Li7'),
        67.75331008246572, rtol=1e-6)
