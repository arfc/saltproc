"""Test basic reprocessing functionality"""
import pytest
import numpy as np
from saltproc.app import reprocess_materials, refill_materials

def test_reprocessing_and_refill(depcode_serpent, proc_test_file, path_test_file):
    mats = depcode_serpent.read_dep_comp(True)
    waste_streams, extracted_mass = reprocess_materials(mats,
                                                        proc_test_file,
                                                        path_test_file)
    np.testing.assert_almost_equal(extracted_mass['fuel'], 1401.0846504569054)
    np.testing.assert_almost_equal(extracted_mass['ctrlPois'], 0.0)
    np.testing.assert_almost_equal(
        waste_streams['fuel']['waste_sparger']['Xe135'],
        11.878661583083327)
    np.testing.assert_almost_equal(
        waste_streams['fuel']['waste_nickel_filter']['I135'],
        0.90990472940444)
    np.testing.assert_almost_equal(
        waste_streams['fuel']['waste_liquid_metal']['Sr90'],
        0.7486923392931839)

    waste_feed_streams = refill_materials(mats, extracted_mass, waste_streams, proc_test_file)
    np.testing.assert_almost_equal(
        waste_feed_streams['fuel']['feed_leu']['U235'],
        43.573521906078334)
    np.testing.assert_almost_equal(
        waste_feed_streams['fuel']['feed_leu']['U238'],
        827.8969156550545)
    np.testing.assert_almost_equal(
        waste_feed_streams['fuel']['feed_leu']['F19'],
        461.8575149906222)
    np.testing.assert_almost_equal(
        waste_feed_streams['fuel']['feed_leu']['Li7'],
        67.75331008246572)


