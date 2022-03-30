from __future__ import absolute_import, division, print_function
from saltproc import DepcodeSerpent, DepcodeOpenMC
from saltproc import Reactor
import json
import openmc as om
import os
import sys
import shutil
import numpy as np

path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))

# global class object
directory = os.path.dirname(path)

# Serpent initalization
serpent = DepcodeSerpent(
    exec_path='sss2',
    template_inputfiles_path=directory +
    '/template.inp',
    geo_files=[
        os.path.join(
            directory,
            '../test_geo.inp')])
serpent.iter_inputfile = directory + '/test'
serpent.iter_matfile = directory + '/material'
geo_test_input = directory + '/test_geometry_switch.inp'

# Openmc initlialization
openmc_input_path = os.path.join(directory, 'test_data/openmc/')
openmc_test_inputfiles = {
    "materials": "test_materials.xml",
    "geometry": "test_geometry.xml",
    "settings": "test_settings.xml",
    "chain_file": "test_chain.xml"
}

openmc_iter_inputfiles = {
    "geometry": "geometry.xml",
    "settings": "settings.xml",
}

# prepend the correct paths to our
# template and iter input files
for key in openmc_test_inputfiles:
    openmc_test_inputfiles[key] = os.path.join(
        openmc_input_path, openmc_test_inputfiles[key])
for key in openmc_iter_inputfiles:
    openmc_iter_inputfiles[key] = os.path.join(
        directory, openmc_iter_inputfiles[key])

openmc = DepcodeOpenMC(
    exec_path='../openmc_deplete.py',
    template_inputfiles_path=openmc_test_inputfiles,
    geo_files=[
        os.path.join(
            openmc_input_path,
            'test_geometry_switch.xml')])
openmc.iter_inputfile = openmc_iter_inputfiles
openmc.iter_matfile = directory + '/materials.xml'


msr = Reactor(volume=1.0,
              power_levels=[1.250E+09, 1.250E+09, 5.550E+09],
              dep_step_length_cumulative=[111.111, 2101.9, 3987.5])


def test_create_nuclide_name_map_zam_to_serpent():
    serpent.create_nuclide_name_map_zam_to_serpent()
    assert serpent.iso_map[380880] == '38088.09c'
    assert serpent.iso_map[962400] == '96240.09c'
    assert serpent.iso_map[952421] == '95342.09c'
    assert serpent.iso_map[340831] == '340831'
    assert serpent.iso_map[300732] == '300732'
    assert serpent.iso_map[511262] == '511262'
    assert serpent.iso_map[420931] == '420931'
    assert serpent.iso_map[410911] == '410911'


def test_convert_nuclide_name_serpent_to_zam():
    assert serpent.convert_nuclide_name_serpent_to_zam(47310) == 471101
    assert serpent.convert_nuclide_name_serpent_to_zam(95342) == 952421
    assert serpent.convert_nuclide_name_serpent_to_zam(61348) == 611481
    assert serpent.convert_nuclide_name_serpent_to_zam(52327) == 521271
    assert serpent.convert_nuclide_name_serpent_to_zam(1001) == 1001
    assert serpent.convert_nuclide_name_serpent_to_zam(1002) == 1002
    assert serpent.convert_nuclide_name_serpent_to_zam(48315) == 481151


def test_read_plaintext_file():
    template_str = serpent.read_plaintext_file(
        serpent.template_inputfiles_path)
    assert template_str[6] == '%therm zrh_h 900 hzr05.32t hzr06.32t\n'
    assert template_str[18] == 'set pop 30 20 10\n'
    assert template_str[22] == 'set bumode  2\n'
    assert template_str[23] == 'set pcc     1\n'


def test_change_sim_par():
    serpent.npop = 1111
    serpent.active_cycles = 101
    serpent.inactive_cycles = 33
    out = serpent.change_sim_par(
        serpent.read_plaintext_file(serpent.template_inputfiles_path)
    )
    assert out[18] == 'set pop %i %i %i\n' % (
        serpent.npop,
        serpent.active_cycles,
        serpent.inactive_cycles)


def test_get_nuc_name():
    assert serpent.get_nuc_name('92235.09c')[0] == 'U235'
    assert serpent.get_nuc_name('38088.09c')[0] == 'Sr88'
    assert serpent.get_nuc_name('95342.09c')[0] == 'Am242m1'
    assert serpent.get_nuc_name('61348.03c')[0] == 'Pm148m1'
    assert serpent.get_nuc_name('20060')[0] == 'He6'
    assert serpent.get_nuc_name('110241')[0] == 'Na24m1'
    assert serpent.get_nuc_name('170381')[0] == 'Cl38m1'
    assert serpent.get_nuc_name('310741')[0] == 'Ga74m1'
    assert serpent.get_nuc_name('290702')[0] == 'Cu70m2'
    assert serpent.get_nuc_name('250621')[0] == 'Mn62m1'
    assert serpent.get_nuc_name('300732')[0] == 'Zn73m2'
    assert serpent.get_nuc_name('370981')[0] == 'Rb98m1'
    assert serpent.get_nuc_name('390972')[0] == 'Y97m2'
    assert serpent.get_nuc_name('491142')[0] == 'In114m2'


def test_read_depcode_info():
    serpent.read_depcode_info()
    assert serpent.sim_info['depcode_name'] == 'Serpent'
    assert serpent.sim_info['depcode_version'] == '2.1.31'
    assert serpent.sim_info['title'] == 'Untitled'
    assert serpent.sim_info['depcode_input_filename'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap'
    assert serpent.sim_info['depcode_working_dir'] == \
        '/home/andrei2/Desktop/git/saltproc/develop/saltproc'
    assert serpent.sim_info['xs_data_path'] == \
        '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata'

    assert serpent.sim_info['MPI_tasks'] == 1
    assert serpent.sim_info['OMP_threads'] == 4
    assert serpent.sim_info['memory_optimization_mode'] == 4
    assert serpent.sim_info['depletion_timestep'] == 3.0


def test_read_depcode_step_param():
    serpent.read_depcode_step_param()
    assert serpent.param['memory_usage'] == [10552.84]
    assert serpent.param['execution_time'] == [81.933]
    assert serpent.param['keff_bds'][0] == 1.00651e+00
    assert serpent.param['keff_eds'][0] == 1.00569e+00
    assert serpent.param['fission_mass_bds'] == [70081]
    assert serpent.param['fission_mass_eds'] == [70077.1]
    assert serpent.param['breeding_ratio'][1] == 5.20000e-04


def test_read_dep_comp():
    mats = serpent.read_dep_comp(True)
    assert mats['fuel']['U235'] == 3499538.3359278883
    assert mats['fuel']['U238'] == 66580417.24509208
    assert mats['fuel']['F19'] == 37145139.35897285
    assert mats['fuel']['Li7'] == 5449107.821098938
    assert mats['fuel']['Cm240'] == 8.787897203694538e-22
    assert mats['fuel']['Pu239'] == 1231.3628804629795
    assert mats['ctrlPois']['Gd155'] == 5812.83289505528
    assert mats['ctrlPois']['O16'] == 15350.701473655872


def test_write_mat_file():
    mats = serpent.read_dep_comp(True)
    iter_matfile_old = serpent.iter_matfile
    serpent.iter_inputfile = serpent.iter_inputfile + '.mat'
    serpent.write_mat_file(mats, 12.0)
    mat_str = serpent.read_plaintext_file(serpent.iter_matfile)
    assert mat_str[0] == '% Material compositions (after 12.000000 days)\n'
    if 'fuel' in mat_str[3]:
        assert mat_str[3].split()[-1] == '2.27175E+07'
        assert mat_str[3].split()[2] == '-4.960200000E+00'
        assert mat_str[1663].split()[-1] == '1.11635E+04'
        assert mat_str[1664] == '            1001.09c  -1.21000137902945E-35\n'
    elif 'ctrlPois' in mat_str[3]:
        assert mat_str[3].split()[-1] == '1.11635E+04'
        assert mat_str[4] == '            1001.09c  -1.21000137902945E-35\n'
    os.remove(serpent.iter_matfile)
    serpent.iter_matfile = iter_matfile_old


def test_insert_path_to_geometry():
    d = serpent.read_plaintext_file(serpent.template_inputfiles_path)
    d_new = serpent.insert_path_to_geometry(d)
    assert d_new[5].split('/')[-1] == 'test_geo.inp"\n'


def test_replace_burnup_parameters():
    time = msr.dep_step_length_cumulative.copy()
    time.insert(0, 0.0)
    depsteps = np.diff(time)
    d = serpent.read_plaintext_file(serpent.template_inputfiles_path)
    for idx in range(len(msr.power_levels)):
        d = serpent.replace_burnup_parameters(d,
                                              msr,
                                              idx)
        out_file = open(serpent.template_inputfiles_path + str(idx), 'w')
        out_file.writelines(d)
        out_file.close()
        d_new = serpent.read_plaintext_file(
            serpent.template_inputfiles_path + str(idx))
        assert d_new[8].split()[4] == 'daystep'
        assert d_new[8].split()[2] == str("%5.9E" % msr.power_levels[idx])
        assert d_new[8].split()[5] == str("%7.5E" % depsteps[idx])
        os.remove(serpent.template_inputfiles_path + str(idx))


def test_create_iter_matfile():
    d = serpent.read_plaintext_file(serpent.template_inputfiles_path)
    out = serpent.create_iter_matfile(d)
    assert out[0].split()[-1] == '\"' + serpent.iter_matfile + '\"'
    os.remove(serpent.iter_matfile)


def _get_iterable_for_object(iterable_object):
    # helper function to DRY
    iterable_type = type(iterable_object)
    if issubclass(
            iterable_type,
            list) or issubclass(
            iterable_type,
            tuple) or issubclass(
                iterable_type,
            np.ndarray):
        if issubclass(iterable_type, np.ndarray):
            iterable_object = iterable_object.flatten()
        iterable = range(0, len(iterable_object))
    elif issubclass(iterable_type, dict):
        iterable = iterable_object
    else:
        raise ValueError(
            f"Iterable of type {type(iterable_object)} is unsupported")
    return iterable


def _check_none_or_iterable_of_ndarray_equal(object1, object2):
    # helper function to DRY
    if issubclass(type(object1), np.ndarray):
        assert (object1 == object2).all()
    elif issubclass(type(object1), tuple) or issubclass(type(object1), list):
        iterable = _get_iterable_for_object(object1)
        for ref in iterable:
            subobject1 = object1[ref]
            subobject2 = object2[ref]
            _check_none_or_iterable_of_ndarray_equal(subobject1, subobject2)
    else:
        assert object1 == object2


def _check_none_or_openmc_object_equal(object1, object2):
    if object1 is None:
        assert object2 is None
    else:
        _check_openmc_objects_equal(object1, object2)


def _check_openmc_objects_equal(object1, object2):
    """
    Helper function for the unit tests to determine equality of
    various OpenMC objects

    Parameters
    ----------
    object1 : openmc.Surface, openmc.Universe, openmc.Cell, openmc.Material, \
    openmc.Lattice
        First openmc object to compare
    object2 :  openmc.Surface, openmc.Universe, openmc.Cell, openmc.Material, \
    openmc.Lattice
        Second openmc object to compare

    """
    try:
        object_type = type(object1)
        assert isinstance(object2, object_type)
        assert object1.id == object2.id
        # this may not apply to all objects.
        assert object1.name == object2.name
        # need to check
        if object_type == om.Material:
            assert object1.density == object2.density
            assert object1.nuclides == object2.nuclides
            assert object1.temperature == object2.temperature
            assert object1.volume == object2.volume
            assert object1._sab == object2._sab

        elif object_type == om.Cell:
            assert object1.fill_type == object2.fill_type
            _check_none_or_openmc_object_equal(object1.fill, object2.fill)
            assert object1.region == object2.region
            _check_none_or_iterable_of_ndarray_equal(
                object1.rotation, object2.rotation)
            _check_none_or_iterable_of_ndarray_equal(
                object1.rotation_matrix, object2.rotation_matrix)
            _check_none_or_iterable_of_ndarray_equal(
                object1.translation, object2.translation)
            assert object1.volume == object2.volume
            # assert object1.atoms == object2.atoms

        elif issubclass(object_type, om.Lattice):
            assert object1.shape == object2.shape
            assert object1.lower_left == object2.lower_left
            assert object1.pitch == object2.pitch
            _check_none_or_openmc_object_equal(object1.outer, object2.outer)
            _check_openmc_iterables_equal(
                {'univ': (object1.universes, object2.universes)})

        elif issubclass(object_type, om.Surface):
            assert object1.boundary_type == object2.boundary_type
            _check_none_or_iterable_of_ndarray_equal(
                object1.coefficients, object2.coefficients)
            assert object1.type == object2.type

        elif object_type == om.Universe:
            _check_openmc_iterables_equal(
                {'cells': (object1.cells, object2.cells)})
            assert object1.volume == object2.volume
            _check_none_or_iterable_of_ndarray_equal(
                object1.bounding_box, object2.bounding_box)
        else:
            raise ValueError(
                f"Object of type {object_type} is not an openmc object.")

    except AssertionError:
        raise AssertionError(
            f"objects of type {object_type} with ids {object1.id} and \
            {object2.id} not equal")


def _check_openmc_iterables_equal(iterable_dict):
    """
    Helper function to check if the given dictionary of iterbales

    Parameters:
    iterable_dict : dict of str to 2-tuple
        Dictionary containing tuples of iterables to compare
    """
    for object_type in iterable_dict:
        object1_iterable, object2_iterable = iterable_dict[object_type]
        assert len(object1_iterable) == len(object2_iterable)
        iterable = _get_iterable_for_object(object1_iterable)
        if issubclass(type(object1_iterable), np.ndarray):
            object1_iterable = object1_iterable.flatten()
            object2_iterable = object2_iterable.flatten()
        for ref in iterable:
            object1 = object2_iterable[ref]
            object2 = object1_iterable[ref]
            _check_openmc_objects_equal(object1, object2)


def test_write_depcode_input():
    # Serpent
    iter_inputfile_old = serpent.iter_inputfile
    serpent.iter_inputfile = serpent.iter_inputfile + '_write_test'
    serpent.write_depcode_input(msr,
                                0,
                                False)
    d = serpent.read_plaintext_file(serpent.iter_inputfile)
    print(d[0])
    assert d[0].split('/')[-2] == 'tests'
    assert d[0].split('/')[-1] == 'material"\n'
    assert d[8].split()[2] == '1.250000000E+09'
    assert d[8].split()[4] == 'daystep'
    assert d[8].split()[-1] == '1.11111E+02'
    assert d[20] == 'set pop 1111 101 33\n'
    os.remove(serpent.iter_inputfile)
    os.remove(serpent.iter_matfile)

    serpent.iter_inputfile = iter_inputfile_old

    # OpenMC
    input_materials = om.Materials.from_xml(
        openmc.template_inputfiles_path['materials'])
    input_geometry = om.Geometry.from_xml(
        openmc.template_inputfiles_path['geometry'],
        materials=input_materials)

    input_cells = input_geometry.get_all_cells()
    input_lattices = input_geometry.get_all_lattices()
    input_surfaces = input_geometry.get_all_surfaces()
    input_universes = input_geometry.get_all_universes()

    openmc.write_depcode_input(msr,
                               0,
                               False)
    # Load in the iter_ objects
    iter_materials = om.Materials.from_xml(openmc.iter_matfile)
    iter_geometry = om.Geometry.from_xml(
        openmc.iter_inputfile['geometry'],
        materials=iter_materials)
    iter_settings = om.Settings.from_xml(openmc.iter_inputfile['settings'])

    iter_cells = iter_geometry.get_all_cells()
    iter_lattices = iter_geometry.get_all_lattices()
    iter_surfaces = iter_geometry.get_all_surfaces()
    iter_universes = iter_geometry.get_all_universes()

    # an easier approach may just be to compare the
    # file contents themselves
    assertion_dict = {'mat': (input_materials, iter_materials),
                      'cells': (input_cells, iter_cells),
                      'lattices': (input_lattices, iter_lattices),
                      'surfs': (input_surfaces, iter_surfaces),
                      'univs': (input_universes, iter_universes)}

    _check_openmc_iterables_equal(assertion_dict)
    assert iter_settings.inactive == openmc.inactive_cycles
    assert iter_settings.batches == openmc.active_cycles + \
        openmc.inactive_cycles
    assert iter_settings.particles == openmc.npop

    del iter_materials, iter_geometry
    del input_materials, input_geometry


def test_write_depletion_settings():
    """
    Unit test for `DepcodeOpenMC.write_depletion_settings`
    """
    openmc.write_depletion_settings(msr, 0)
    with open(openmc.iter_inputfile['depletion_settings']) as f:
        j = json.load(f)
        assert j['directory'] == directory
        assert j['timesteps'][0] == msr.dep_step_length_cumulative[0]
        assert j['operator_kwargs']['chain_file'] == \
            openmc.template_inputfiles_path['chain_file']
        assert j['integrator_kwargs']['power'] == msr.power_levels[0]
        assert j['integrator_kwargs']['timestep_units'] == 'd'


def test_write_saltproc_openmc_tallies():
    """
    Unit test for `DepcodeOpenMC.write_saltproc_openmc_tallies`
    """

    mat = om.Materials.from_xml(openmc.template_inputfiles_path['materials'])
    geo = om.Geometry.from_xml(
        openmc.template_inputfiles_path['geometry'], mat)
    openmc.write_saltproc_openmc_tallies(mat, geo)
    del mat, geo
    tallies = om.Tallies.from_xml(openmc.iter_inputfile['tallies'])

    # now write asserts statements based on the openmc.Tallies API and
    # what we expect our tallies to be
    assert len(tallies) == 5
    tal0 = tallies[0]
    tal1 = tallies[1]
    tal2 = tallies[2]
    tal3 = tallies[3]
    tal4 = tallies[4]

    assert tal0.name == 'delayed-fission-neutrons'
    assert isinstance(tal0.filters[0], om.DelayedGroupFilter)
    assert tal0.scores[0] == 'delayed-nu-fission'
    assert tal1.name == 'total-fission-neutrons'
    assert isinstance(tal1.filters[0], om.UniverseFilter)
    assert tal1.scores[0] == 'nu-fission'
    assert tal2.name == 'precursor-decay-constants'
    assert isinstance(tal2.filters[0], om.DelayedGroupFilter)
    assert tal2.scores[0] == 'decay-rate'
    assert tal3.name == 'fission-energy'
    assert isinstance(tal3.filters[0], om.UniverseFilter)
    assert tal3.scores[0] == 'fission-q-recoverable'
    assert tal3.scores[1] == 'fission-q-prompt'
    assert tal3.scores[2] == 'kappa-fission'
    assert tal4.name == 'normalization-factor'
    assert isinstance(tal4.filters[0], om.UniverseFilter)
    assert tal4.scores[0] == 'heating'


def test_switch_to_next_geometry():
    # Serpent
    shutil.copy2(geo_test_input, serpent.iter_inputfile + '_test')
    iter_inputfile_old = serpent.iter_inputfile
    serpent.iter_inputfile = serpent.iter_inputfile + '_test'
    serpent.geo_files += ['../../examples/406.inp', '../../examples/988.inp']
    serpent.switch_to_next_geometry()
    d = serpent.read_plaintext_file(serpent.iter_inputfile)
    assert d[5].split('/')[-1] == '988.inp"\n'
    os.remove(serpent.iter_inputfile)
    serpent.iter_inputfile = iter_inputfile_old

    # OpenMC
    mat = om.Materials.from_xml(openmc.template_inputfiles_path['materials'])
    expected_geometry = om.Geometry.from_xml(openmc.geo_files[0], mat)
    expected_cells = expected_geometry.get_all_cells()
    expected_lattices = expected_geometry.get_all_lattices()
    expected_surfaces = expected_geometry.get_all_surfaces()
    expected_universes = expected_geometry.get_all_universes()
    del expected_geometry

    openmc.switch_to_next_geometry()
    switched_geometry = om.Geometry.from_xml(
        openmc.iter_inputfile['geometry'], mat)

    switched_cells = switched_geometry.get_all_cells()
    switched_lattices = switched_geometry.get_all_lattices()
    switched_surfaces = switched_geometry.get_all_surfaces()
    switched_universes = switched_geometry.get_all_universes()
    del switched_geometry

    assertion_dict = {'cells': (expected_cells, switched_cells),
                      'lattices': (expected_lattices, switched_lattices),
                      'surfs': (expected_surfaces, switched_surfaces),
                      'univs': (expected_universes, switched_universes)}

    _check_openmc_iterables_equal(assertion_dict)

    del mat
