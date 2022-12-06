import json
from pathlib import Path

import numpy as np
import pytest
import openmc

from saltproc import Reactor


@pytest.fixture
def geometry_switch(scope='module'):
    path = Path(__file__).parents[2]
    return (path / 'openmc_data' / 'geometry_switch.xml')


@pytest.fixture
def msr(scope='module'):
    reactor = Reactor(volume=1.0,
                      power_levels=[1.250E+09, 1.250E+09, 5.550E+09],
                      dep_step_length_cumulative=[111.111, 2101.9, 3987.5])
    return reactor


def test_write_runtime_input(openmc_depcode, msr):
    # OpenMC
    input_materials = openmc.Materials.from_xml(
        openmc_depcode.template_input_file_path['materials'])
    input_geometry = openmc.Geometry.from_xml(
        openmc_depcode.geo_files[0],
        materials=input_materials)

    input_cells = input_geometry.get_all_cells()
    input_lattices = input_geometry.get_all_lattices()
    input_surfaces = input_geometry.get_all_surfaces()
    input_universes = input_geometry.get_all_universes()

    openmc_depcode.write_runtime_input(msr,
                                       0,
                                       False)
    # Load in the runtime_ objects
    runtime_materials = openmc.Materials.from_xml(openmc_depcode.runtime_matfile)
    runtime_geometry = openmc.Geometry.from_xml(
        openmc_depcode.runtime_inputfile['geometry'],
        materials=runtime_materials)
    runtime_settings = openmc.Settings.from_xml(
        openmc_depcode.runtime_inputfile['settings'])

    runtime_cells = runtime_geometry.get_all_cells()
    runtime_lattices = runtime_geometry.get_all_lattices()
    runtime_surfaces = runtime_geometry.get_all_surfaces()
    runtime_universes = runtime_geometry.get_all_universes()

    # an easier approach may just be to compare the
    # file contents themselves
    assertion_dict = {'mat': (input_materials, runtime_materials),
                      'cells': (input_cells, runtime_cells),
                      'lattices': (input_lattices, runtime_lattices),
                      'surfs': (input_surfaces, runtime_surfaces),
                      'univs': (input_universes, runtime_universes)}

    _check_openmc_iterables_equal(assertion_dict)
    assert runtime_settings.inactive == openmc_depcode.inactive_cycles
    assert runtime_settings.batches == openmc_depcode.active_cycles + \
        openmc_depcode.inactive_cycles
    assert runtime_settings.particles == openmc_depcode.npop

    del runtime_materials, runtime_geometry
    del input_materials, input_geometry


def test_write_depletion_settings(openmc_depcode, msr):
    """
    Unit test for `Depcodeopenmc_depcode.write_depletion_settings`
    """
    openmc_depcode.write_depletion_settings(msr, 0)
    with open(openmc_depcode.runtime_inputfile['depletion_settings']) as f:
        j = json.load(f)
        assert j['directory'] == str(Path(
            openmc_depcode.runtime_inputfile['settings']).parents[0])
        assert j['timesteps'][0] == msr.dep_step_length_cumulative[0]
        assert j['operator_kwargs']['chain_file'] == \
            openmc_depcode.template_input_file_path['chain_file']
        assert j['integrator_kwargs']['power'] == msr.power_levels[0]
        assert j['integrator_kwargs']['timestep_units'] == 'd'


def test_write_saltproc_openmc_tallies(openmc_depcode):
    """
    Unit test for `OpenMCDepcode.write_saltproc_openmc_tallies`
    """

    mat = openmc.Materials.from_xml(
        openmc_depcode.template_input_file_path['materials'])
    geo = openmc.Geometry.from_xml(
        openmc_depcode.geo_files[0], mat)
    openmc_depcode.write_saltproc_openmc_tallies(mat, geo)
    del mat, geo
    tallies = openmc.Tallies.from_xml(openmc_depcode.runtime_inputfile['tallies'])

    # now write asserts statements based on the openmc_depcode.Tallies API and
    # what we expect our tallies to be
    assert len(tallies) == 5
    tal0 = tallies[0]
    tal1 = tallies[1]
    tal2 = tallies[2]
    tal3 = tallies[3]
    tal4 = tallies[4]

    assert tal0.name == 'delayed-fission-neutrons'
    assert isinstance(tal0.filters[0], openmc.DelayedGroupFilter)
    assert tal0.scores[0] == 'delayed-nu-fission'
    assert tal1.name == 'total-fission-neutrons'
    assert isinstance(tal1.filters[0], openmc.UniverseFilter)
    assert tal1.scores[0] == 'nu-fission'
    assert tal2.name == 'precursor-decay-constants'
    assert isinstance(tal2.filters[0], openmc.DelayedGroupFilter)
    assert tal2.scores[0] == 'decay-rate'
    assert tal3.name == 'fission-energy'
    assert isinstance(tal3.filters[0], openmc.UniverseFilter)
    assert tal3.scores[0] == 'fission-q-recoverable'
    assert tal3.scores[1] == 'fission-q-prompt'
    assert tal3.scores[2] == 'kappa-fission'
    assert tal4.name == 'normalization-factor'
    assert isinstance(tal4.filters[0], openmc.UniverseFilter)
    assert tal4.scores[0] == 'heating'


def test_switch_to_next_geometry(openmc_depcode):
    # OpenMC
    mat = openmc.Materials.from_xml(
        openmc_depcode.template_input_file_path['materials'])
    expected_geometry = openmc.Geometry.from_xml(
        openmc_depcode.geo_files[0], mat)
    expected_cells = expected_geometry.get_all_cells()
    expected_lattices = expected_geometry.get_all_lattices()
    expected_surfaces = expected_geometry.get_all_surfaces()
    expected_universes = expected_geometry.get_all_universes()
    del expected_geometry

    openmc_depcode.switch_to_next_geometry()
    switched_geometry = openmc.Geometry.from_xml(
        openmc_depcode.runtime_inputfile['geometry'], mat)

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


def _check_openmc_iterables_equal(iterable_dict):
    """
    Helper function to check equality iterables contained in a dictionary.

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


def _check_openmc_objects_equal(object1, object2):
    """
    Helper function for the unit tests to determine equality of
    various OpenMC objects

    Parameters
    ----------
    object1 : openmc_depcode.Surface, \
    openmc_depcode.Universe, \
    openmc_depcode.Cell, \
    openmc_depcode.Material, \
    openmc_depcode.Lattice
        First openmc object to compare
    object2 :  openmc_depcode.Surface, \
    openmc_depcode.Universe, \
    openmc_depcode.Cell, \
    openmc_depcode.Material, \
    openmc_depcode.Lattice
        Second openmc object to compare

    """
    try:
        object_type = type(object1)
        assert isinstance(object2, object_type)
        assert object1.id == object2.id
        assert object1.name == object2.name
        if object_type == openmc.Material:
            assert object1.density == object2.density
            assert object1.nuclides == object2.nuclides
            assert object1.temperature == object2.temperature
            assert object1.volume == object2.volume
            assert object1._sab == object2._sab

        elif object_type == openmc.Cell:
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

        elif issubclass(object_type, openmc.Lattice):
            assert object1.shape == object2.shape
            assert object1.lower_left == object2.lower_left
            assert object1.pitch == object2.pitch
            _check_none_or_openmc_object_equal(object1.outer, object2.outer)
            _check_openmc_iterables_equal(
                {'univ': (object1.universes, object2.universes)})

        elif issubclass(object_type, openmc.Surface):
            assert object1.boundary_type == object2.boundary_type
            _check_none_or_iterable_of_ndarray_equal(
                object1.coefficients, object2.coefficients)
            assert object1.type == object2.type

        elif object_type == openmc.Universe:
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


def _check_none_or_openmc_object_equal(object1, object2):
    if object1 is None:
        assert object2 is None
    else:
        _check_openmc_objects_equal(object1, object2)


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
