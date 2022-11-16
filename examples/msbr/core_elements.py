import openmc
import numpy as np

def _bound_zone_cells(cells_tuples, levels):
    """Helper function that moves Zone IB and Zone IIA cells to the
    appropriate height."""
    cell_list = []
    n_levels = len(cells_tuples)
    for i, cells in enumerate(cells_tuples):
        if i == 0:
            lower_bound = None
            upper_bound = levels[i]
        elif i == n_levels - 1:
            lower_bound = levels[i-1]
            upper_bound = None
        else:
            lower_bound = levels[i-1]
            upper_bound = levels[i]
        for j, cell in enumerate(cells):
            if lower_bound is None:
                cell.region = cell.region & -upper_bound
            elif upper_bound is None:
                cell.region = cell.region & +lower_bound
            else:
                cell.region = cell.region & +lower_bound & -upper_bound
            cell_list.append(cell)
    return cell_list

def zoneIB(gr_sq_neg,
           gr_extra_regions,
           inter_elem_channel,
           gr_round_4,
           moder,
           fuel,
           hast):
    """Create universe for Zone IB element. Based on specification in
    Robertson, 1971 Fig 3.4 (p. 17)

    Parameters
    ----------
    gr_sq_neg : openmc.Intersection
        The region bounding the outer surface of the 4 in. x 4 in. graphite
        element.
    gr_extra_regions : list of (openmc.Region, str)
        'Add-on' regions and their names for the graphite element.
        Includes ribs, rib tips, and gap-filling regions.
    inter_elem_channel : openmc.Region, list of (openmc.Region, str)
        Inter-element channel region(s).
    gr_round_4 : openmc.ZCylinder
        Outer bounding surface for cylindrical graphite in uppermost part of
        element.
    fuel : openmc.Material
        Fuel salt material
    moder : openmc.Material
        Graphite material
    hast : openmc.Material
        Hastelloy-N material.

    Returns
    -------
    ib : openmc.Universe
        Universe for Zone IB element.
    """
    elem_levels = [22.86, 419.10, 438.15, 445.135]
    level_bounds = []
    for level in elem_levels:
        level_bounds.append(openmc.ZPlane(z0=level))
    s1 = openmc.ZCylinder(r=4.953, name='ib_gr_round_1')
    s2 = openmc.ZCylinder(r=1.71069, name='ib_fuel_hole')

    h = 12.66
    theta = np.arctan(4.953 / h)
    r2 = (1 / np.cos(theta))**2 - 1
    s3 = openmc.ZCone(z0=h + elem_levels[2], r2=r2, name='cone_i')

    c1 = openmc.Cell(fill=fuel, region=(-s2), name='ib_fuel_inner_1')
    c2 = openmc.Cell(fill=moder, region=(+s2 & -s1), name='ib_moderator_1')
    c3 = openmc.Cell(fill=fuel, region=(+s1), name='ib_fuel_outer_1')
    ib1 = (c1, c2, c3)

    # I-A  main (lower 2)
    c4 = c1.clone(clone_materials=False)
    c4.name = 'ib_fuel_inner_main'

    c5 = openmc.Cell(fill=moder, region=(+s2 &
                                         gr_sq_neg &
                                         inter_elem_channel),
                     name='ib_moderator_main')
    c6 = openmc.Cell(fill=fuel, region=(~gr_sq_neg & inter_elem_channel),
                     name='ib_fuel_outer_main')
    ibm = [c4, c5, c6]

    for (reg, name) in gr_extra_regions:
            ibm.append(openmc.Cell(fill=moder, region=reg,
                                   name=f'ib_moderator_main_{name}'))


    # I-A 2 (upper 1)
    c7 = c1.clone(clone_materials=False)
    c8 = c2.clone(clone_materials=False)
    c9 = c3.clone(clone_materials=False)
    c7.name = 'ib_fuel_inner_2'
    c8.name = 'ib_moderator_2'
    c9.name = 'ib_fuel_outer_2'

    ib2 = (c7, c8, c9)

    # I-A 3 (upper 2)
    c10 = c1.clone(clone_materials=False)
    c10.name = 'ib_fuel_inner_3'
    c11 = openmc.Cell(fill=moder, region=(+s2 & -s3), name='ib_moderator_3')
    c12 = openmc.Cell(fill=fuel, region=(+s3), name='ib_fuel_outer_3')
    ib3 = (c10, c11, c12)

    # I-A 4 (upper 3)
    c13 = openmc.Cell(fill=hast, region=(-s2),
                      name='ib_hast')
    c14 = openmc.Cell(fill=moder, region=(+s2 & -gr_round_4),
                      name='ib_moderator_4')
    c15 = openmc.Cell(fill=fuel, region=(+gr_round_4),
                      name='ib_fuel_outer_4')
    ib4 = (c13, c14, c15)

    elem_cells = [ib1, ibm, ib2, ib3, ib4]
    # universe_id=1
    ib = openmc.Universe(name='zone_ib')
    ib.add_cells(_bound_zone_cells(elem_cells, level_bounds))
    return ib

def zoneIIA(gr_sq_neg,
            gr_extra_regions,
            inter_elem_channel,
            gr_round_4,
            moder,
            fuel):
    """Create universe for Zone IIA element. Based on specification in
    Robertson, 1971 Fig 3.5 (p. 18)

    Parameters
    ----------
    gr_sq_neg : openmc.Intersection
        The region bounding the outer surface of the 4 in. x 4 in. graphite
        element.
    gr_extra_regions : list of (openmc.Region, str)
        'Add-on' regions and their names for the graphite element.
        Includes ribs, rib tips, and gap-filling regions.
    inter_elem_channel : openmc.Region, list of (openmc.Region, str)
        Inter-element channel region(s).
    gr_round_4 : openmc.ZCylinder
        Outer bounding surface for cylindrical graphite in uppermost part of
        element.
    fuel : openmc.Material
        Fuel salt material
    moder : openmc.Material
        Graphite material
    hast : openmc.Material
        Hastelloy-N material.

    Returns
    -------
    iia : openmc.Universe
        Universe for Zone IIA element.
    """

    elem_levels = [434.34, 436.88, 439.42, 441.96]
    level_bounds = []
    for level in elem_levels:
        level_bounds.append(openmc.ZPlane(z0=level))
    s1 = openmc.ZCylinder(r=3.302, name='iia_fuel_hole_main') # Hole with fuel salt - Fig 3.5, Roberton 1971 (3.27787 - p.47)
    s2 = openmc.ZCylinder(r=0.635, name='iia_fuel_hole_2')
    s3 = openmc.ZCylinder(r=3.65125, name='iia_gr_round_3')
    h = 6.5
    theta = np.arctan(3.65125 / h)
    r2 = (1 / np.cos(theta))**2 - 1
    s4 = openmc.ZCone(z0=h + elem_levels[2], r2=r2, name='cone_ii')


    # II-A main (lower 1)
    c1 = openmc.Cell(fill=fuel, region=(-s1), name='iia_fuel_inner_main')
    c2 = openmc.Cell(fill=moder, region=(+s1 &
                                         gr_sq_neg &
                                         inter_elem_channel),
                     name='iia_moderator_main')
    c3 = openmc.Cell(fill=fuel, region=(~gr_sq_neg & inter_elem_channel),
                     name='iia_fuel_outer_main')
    iiam = [c1, c2, c3]


    # II-A 2 (upper 1)
    c4 = openmc.Cell(fill=fuel, region=(-s2), name='iia_fuel_inner_2')
    c5 = openmc.Cell(fill=moder, region=(+s2 &
                                         gr_sq_neg &
                                         inter_elem_channel),
                     name='iia_moderator_2')
    c6 = c3.clone(clone_materials=False)
    c6.name = 'iia_fuel_outer_2'
    iia2 = [c4, c5, c6]

    for (reg, name) in gr_extra_regions:
        iiam.append(openmc.Cell(fill=moder, region=reg,
                                name=f'iia_moderator_main_{name}'))
        iia2.append(openmc.Cell(fill=moder, region=reg,
                                name=f'iia_moderator_2_{name}'))

    # II-A 3 (upper 2)
    c7 = c4.clone(clone_materials=False)
    c7.name = 'iia_fuel_inner_3'
    c8 = openmc.Cell(fill=moder, region=(+s2 & -s3), name='iia_moderator_3')
    c9 = openmc.Cell(fill=fuel, region=(+s3), name='iia_fuel_outer_3')
    iia3 = (c7, c8, c9)

    # II-A 4 (upper 3)
    c10 = openmc.Cell(fill=moder, region=(-s4), name='iia_moderator_4')
    c11 = openmc.Cell(fill=fuel, region=(+s4), name='iia_fuel_outer_4')
    iia4 = (c10, c11)

    # II-A 5 (upper 4)
    c12 = openmc.Cell(fill=moder, region=(-gr_round_4), name='iia_moderator_5')
    c13 = openmc.Cell(fill=fuel, region=(+gr_round_4), name='iia_fuel_outer_5')
    iia5 = (c12, c13)

    elem_cells = [iiam, iia2, iia3, iia4, iia5]
    # universe_id=2
    iia = openmc.Universe(name='zone_iia')
    iia.add_cells(_bound_zone_cells(elem_cells, level_bounds))
    return iia

def void_cell():
    """Creates a void cell universe for filling unused parts of core lattice.

    Returns
    -------
    v : openmc.Universe
        Void universe
    """
    c1 = openmc.Cell(name='lattice_void')
    #universe_id=5
    v = openmc.Universe(name='lattice_void')
    v.add_cell(c1)
    return v

def graphite_triangles(fuel, moder):
    """Creates triangular prism elements that fill in 90-degree corners
    on the outermost layer of Zone IIA,

    Parameters
    ----------
    fuel : openmc.Material
        Fuel salt material
    moder : openmc.Material
        Graphite material

    Returns
    -------
    tri_univs : list of openmc.Universe
        Universes for graphite trangular prism elements.

    """
    s1 = openmc.Plane(1.0, 1.0, 0.0, 0.0)
    s2 = openmc.Plane(-1.0, 1.0, 0.0, 0.0)
    s3 = openmc.Plane(1.0, -1.0, 0.0, 0.0)
    s4 = openmc.Plane(-1.0, -1.0, 0.0, 0.0)
    surfs = [(s4, 'bottom_left'),
             (s1, 'top_right'),
             (s2, 'top_left'),
             (s3, 'bottom_right')]
    tri_univs = []
    for i, (s, name) in enumerate(surfs):
        c1 = openmc.Cell(fill=moder, region=(-s))
        c2 = openmc.Cell(fill=fuel, region=(+s))
        # universe_id = 6+i
        gr_tri = openmc.Universe(name=f'{name}_triangle')
        gr_tri.add_cells([c1, c2])
        tri_univs.append(gr_tri)
    return tri_univs
