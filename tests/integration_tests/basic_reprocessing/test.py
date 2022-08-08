"""Test basic reprocessing functionality"""
from pathlib import Path

import pytest
from saltproc.app import read_main_input, _create_depcode_object
from saltproc.app import reprocessing, refill

@pytest.fixture
def setup():
    path = Path(__file__).parents[2]
    saltproc_input = (path / 'serpent_data' / 'test_input.json').as_posix()
    _, process_input_file, path_input_file, object_input = read_main_input(saltproc_input)
    depcode = _create_depcode_object(object_input[0])
    depcode.iter_inputfile = (path / 'serpent_data' / 'ref').as_posix()

    return depcode, process_input_file, path_input_file

def test_reprocessing_and_refill(setup):
    depcode, proccess_input_file, path_input_file = setup
    mats = depcode.read_dep_comp(True)
    waste_streams, extracted_mass = reprocessing(mats,
                                                     proccess_input_file,
                                                     path_input_file)
    assert extracted_mass['fuel'] == 1401.0846504569054
    assert extracted_mass['ctrlPois'] == 0.0
    assert waste_streams['fuel']['waste_sparger']['Xe135'] == 11.878661583083327
    assert waste_streams['fuel']['waste_nickel_filter']['I135'] == 0.90990472940444
    assert waste_streams['fuel']['waste_liquid_metal']['Sr90'] == 0.7486923392931839

    waste_feed_streams = refill(mats, extracted_mass, waste_streams, proccess_input_file)
    assert waste_feed_streams['fuel']['feed_leu']['U235'] == 43.573521906078334
    assert waste_feed_streams['fuel']['feed_leu']['U238'] == 827.8969156550545
    assert waste_feed_streams['fuel']['feed_leu']['F19'] == 461.8575149906222
    assert waste_feed_streams['fuel']['feed_leu']['Li7'] == 67.75331008246572
