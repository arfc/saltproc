path = os.path.dirname(os.path.dirname(__file__))
# global class object
directory = os.path.dirname(path)
iter_inputfile = directory + '/test'
main_input = directory + '/test.json'
dot_input = directory + '/test.dot'

serpent = DepcodeSerpent(exec_path='sss2',
                         template_input_file_path=directory + '/template.inp',
                         geo_files=None)
serpent.iter_inputfile = iter_inputfile
serpent.iter_matfile = directory + '/material'



def test_reprocessing():
    mats = serpent.read_dep_comp(True)
    waste_st, rem_mass = app.reprocessing(mats)
    assert rem_mass['fuel'] == 1401.0846504569054
    assert rem_mass['ctrlPois'] == 0.0
    assert waste_st['fuel']['waste_sparger']['Xe135'] == 11.878661583083327
    assert waste_st['fuel']['waste_nickel_filter']['I135'] == 0.90990472940444
    assert waste_st['fuel']['waste_liquid_metal']['Sr90'] == 0.7486923392931839

def test_refill():
    mats = serpent.read_dep_comp(True)
    waste_st, rem_mass = app.reprocessing(mats)
    m_after_refill = app.refill(mats, rem_mass, waste_st)
    assert m_after_refill['fuel']['feed_leu']['U235'] == 43.573521906078334
    assert m_after_refill['fuel']['feed_leu']['U238'] == 827.8969156550545
    assert m_after_refill['fuel']['feed_leu']['F19'] == 461.8575149906222
    assert m_after_refill['fuel']['feed_leu']['Li7'] == 67.75331008246572
