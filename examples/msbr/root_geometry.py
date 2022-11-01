import openmc
import numpy as np

def shared_root_geometry():
    """Creates surfaces and regions for root geometry.

    Returns
    -------
    zone_bounds : tuple
        Tuple containing zone bounding surfaces
    core_bounds : list of openmc.Surface
        List of reactor core bounding surfaces
    reflector_bounds : list of openmc.Surface
        List of reflector boundng surfaces
    vessel_bounds : list of openmc.Surface
        List of reactor vessel bounding surfaces

    """
    cr_boundary = openmc.model.rectangular_prism(15.24*2, 15.24*2)
    core_base = openmc.ZPlane(z0=0.0, name='core_base')
    core_top = openmc.ZPlane(z0=449.58, name='core_top')

    s1 = openmc.model.IsogonalOctagon(center=(0.0,0.0), r1=208.28, r2=222.71,
                                      name='base_octader')
    s2 = openmc.model.IsogonalOctagon(center=(0.0,0.0), r1=218.44, r2=215.53,
                                      name='smaller_octader')
    s3 = openmc.model.IsogonalOctagon(center=(0.0,0.0), r1=228.60, r2=193.97,
                                      name='smallest_octader')

    zone_i_boundary = (s1, s2, s3)

    zone_ii_boundary = openmc.ZCylinder(r=256.032, name='iib_boundary')
    annulus_boundary = openmc.ZCylinder(r=261.112, name='annulus_boundary')
    lower_plenum_boundary = openmc.ZPlane(z0=-7.62,
                                          name='lower_plenum_boundary')

    zone_bounds = (cr_boundary,
                   zone_i_boundary,
                   zone_ii_boundary)
    core_bounds = (annulus_boundary,
                   lower_plenum_boundary,
                   core_base,
                   core_top)
    radial_reflector_boundary = \
        openmc.ZCylinder(r=338.328, name='radial_reflector_boundary')
    bottom_reflector_boundary = \
        openmc.ZPlane(z0=-76.2, name='bottom_axial_reflector_boundary')
    top_reflector_boundary = \
        openmc.ZPlane(z0=525.78, name='top_axial_reflector_boundary')
    reflector_bounds = (radial_reflector_boundary,
                        bottom_reflector_boundary,
                        top_reflector_boundary)

    radial_vessel_boundary = openmc.ZCylinder(r=343.408,
                                              name='radial_vessel_wall',
                                              boundary_type='vacuum')
    bottom_vessel_boundary = openmc.ZPlane(z0=-81.28,
                                           name='bottom_vessel_wall',
                                           boundary_type='vacuum')
    top_vessel_boundary = openmc.ZPlane(z0=530.86,
                                        name='top_vessel_wall',
                                        boundary_type='vacuum')

    vessel_bounds = (radial_vessel_boundary,
                     bottom_vessel_boundary,
                     top_vessel_boundary)

    return zone_bounds, core_bounds, reflector_bounds, vessel_bounds

def zoneIIB(zone_i_boundary,
            zone_ii_boundary,
            core_base,
            core_top,
            fuel,
            moder):
    """ Creates Zone IIB graphite slab elements.

    Parameters
    ----------
    zone_i_boundary : 3-tuple of openmc.model.IsogonalOctagon
        Zone I bounding surfaces in the xy-plane
    zone_ii_boundary : openmc.ZCylinder
        Zone II bounding surface in the xy-plance
    core_base : openmc.ZPlane
        Core bottom bounding surface.
    core_top : openmc.ZPlane
        Core top bounding surface.
    fuel : openmc.Material
        Fuel salt material
    moder : openmc.Material
        Graphite material

    Returns
    -------
    iib_cells : list of openmc.Cell
        Cells containing graphite slabs in Zone IIB.
    """


    # Large elements
    large_angular_width = 3.538
    large_half_w = large_angular_width / 2
    large_positions = np.linspace(0, 315, 8)
    r_outer = 256.032
    r_big1 = 229.6
    r_big2 = 223.6
    rb_1 = (r_big1, r_outer)
    rb_2 = (r_big2, r_outer)
    big_radii = [rb_1, rb_2] * 4
    small_radii = (207.28, r_outer)

    r_hole = 3.0875
    hole_args = ({'x0': 242.679, 'y0': 0.0, 'r': r_hole},
                 {'x0': 171.60, 'y0': 171.60, 'r': r_hole},
                 {'x0': 0.0, 'y0': 242.679, 'r': r_hole},
                 {'x0': -171.60, 'y0': 171.60, 'r': r_hole},
                 {'x0': -242.679, 'y0': 0.0, 'r': r_hole},
                 {'x0': -171.60, 'y0': -171.60, 'r': r_hole},
                 {'x0': 0.0, 'y0': -242.697, 'r': r_hole},
                 {'x0': 171.60, 'y0': -171.60, 'r': r_hole})

    # Small elements
    small_angular_width = 0.96
    adjacent_angular_offset = 0.675 #27/40
    small_elems_per_octant = 25

    elem_cells = []
    zone_iib_reg = None
    for i, pos in enumerate(large_positions):
        pos = np.round(pos, 3)
        r1_big, r2_big = big_radii[i]
        t1_big = np.round(pos - large_half_w, 3)
        t2_big = np.round(pos + large_half_w, 3)
        s1 = openmc.model.CylinderSector(r1_big,
                                         r2_big,
                                         t1_big,
                                         t2_big,
                                         name=f'iib_large_element_{pos}')
        s2 = openmc.ZCylinder(**hole_args[i])

        elem_cells.append(openmc.Cell(fill=moder, region=(-s1 & +s2),
                                      name=f'iib_large_element_{pos}'))
        elem_cells.append(openmc.Cell(fill=fuel, region=(-s2),
                                      name=('iib_large_element'
                                            f'_fuel_hole_{pos}')))

        t1_small = np.round(t2_big + adjacent_angular_offset, 3)
        r1_small, r2_small = small_radii

        if isinstance(zone_iib_reg, openmc.Region):
            zone_iib_reg = zone_iib_reg & +s1
        else:
            zone_iib_reg = +s1

        for i in range(0, small_elems_per_octant):
            t2_small = np.round(t1_small + small_angular_width, 3)

            # reflector element
            pos = t2_small - (small_angular_width / 2)
            pos = np.round(pos, 3)
            s5 = openmc.model.CylinderSector(r1_small,
                                             r2_small,
                                             t1_small,
                                             t2_small,
                                             name=f'iib_small_element_{pos}')
            elem_cells.append(openmc.Cell(fill=moder, region=-s5,
                                          name=f'iib_small_element_{pos}'))

            t1_small = np.round(t2_small + adjacent_angular_offset, 3)

            zone_iib_reg = zone_iib_reg & +s5

    #universe_id=10
    iib = openmc.Universe(name='zone_iib', cells=elem_cells)
    s1, s2, s3 = zone_i_boundary

    iib.add_cell(openmc.Cell(fill=fuel, region=zone_iib_reg,
                             name='zone_iib_fuel'))
    iib_cells = [openmc.Cell(fill=iib, region=(+s1 & +s2 & +s3 &
                                               -zone_ii_boundary &
                                               +core_base &
                                               -core_top),
                             name='zone_iib')]
    return iib_cells

def annulus(zone_ii_boundary, annulus_boundary, core_base, core_top, fuel):
    """ Creates annulus cell.

    Parameters
    ----------
    zone_ii_boundary : openmc.ZCylinder
        Zone II bounding surfaces in the xy-plane
    annulus_boundary : openmc.ZCylinder
        Annulus bounding surface in the xy-plance
    core_base : openmc.ZPlane
        Core bottom bounding surface.
    core_top : openmc.ZPlane
        Core top bounding surface.
    fuel : openmc.Material
        Fuel salt material

    Returns
    -------
    c1 : openmc.Cell
        Annulus cell.
    """
    annulus_reg = +zone_ii_boundary & -annulus_boundary & +core_base & -core_top
    c1 = openmc.Cell(fill=fuel, region=annulus_reg, name='annulus')
    return c1

def lower_plenum(core_base, lower_plenum_boundary, annulus_boundary, fuel):
    """ Creates lower plenum cell.

    Parameters
    ----------
    core_base : openmc.ZPlane
        Core bottom bounding surface.
    lower_plenum_boundary : openmc.ZPlane
        Lower plenum bottom bounding surface.
    annulus_boundary : openmc.ZCylinder
        Annulus bounding surface in the xy-plance
    fuel : openmc.Material
        Fuel salt material

    Returns
    -------
    c1 : openmc.Cell
        Lower plenum cell
    """
    lower_plenum_reg = -core_base & +lower_plenum_boundary & -annulus_boundary
    c1 = openmc.Cell(fill=fuel, region=lower_plenum_reg, name='lower_plenum')
    return c1

def reflectors(annulus_boundary,
               radial_reflector_boundary,
               lower_plenum_boundary,
               bottom_reflector_boundary,
               core_top,
               top_reflector_boundary,
               moder):
    """ Creates graphite reflector cells.

    Parameters
    ----------
    annulus_boundary : openmc.ZCylinder
        Annulus bounding surface in the xy-plance
    radial_reflector_boundary : openmc.ZCylinder
        Reflector bounding surface in the xy-plance
    lower_plenum_boundary : openmc.ZPlane
        Lower plenum bottom bounding surface.
    bottom_reflector_boundary : openmc.ZPlane
        Reflector bottom bounding surface.
    core_top : openmc.ZPlane
        Core top bounding surface.
    top_reflector_boundary : openmc.ZPlane
        Reflector top bounding surface.
    moder : openmc.Material
        Graphite material

    Returns
    -------
    c1 : openmc.Cell
        Radial reflector.
    c2 : openmc.Cell
        Bottom axial reflector.
    c3 : openmc.Cell
        Top axial reflector.
    """
    radial_reflector_reg = (+annulus_boundary &
                            -radial_reflector_boundary &
                            +bottom_reflector_boundary &
                            -top_reflector_boundary)
    bottom_reflector_reg = (-annulus_boundary &
                            -lower_plenum_boundary &
                            +bottom_reflector_boundary)
    top_reflector_reg = (-annulus_boundary &
                         +core_top &
                         -top_reflector_boundary)

    c1 = openmc.Cell(fill=moder, region=radial_reflector_reg,
                     name='radial_reflector')
    c2 = openmc.Cell(fill=moder, region=bottom_reflector_reg,
                     name='bottom_axial_reflector')
    c3 = openmc.Cell(fill=moder, region=top_reflector_reg,
                     name='top_axial_reflector')
    return c1, c2, c3

def vessel(radial_reflector_boundary,
           radial_vessel_boundary,
           bottom_vessel_boundary,
           top_vessel_boundary,
           top_reflector_boundary,
           bottom_reflector_boundary,
           hast):
    """ Creates reactor vessel cells.

    Parameters
    ----------
    radial_reflector_boundary : openmc.ZCylinder
        Reflector bounding surface in the xy-plance
    radial_vessel_boundary : openmc.ZCylinder
        Vessel bounding surface in the xy-plane
    bottom_vessel_boundary : openmc.ZPlane
        Vessel bottom bounding surface.
    top_vessel_boundary : openmc.ZPlane
        Vessel top bounding surface.
    top_reflector_boundary : openmc.ZPlane
        Reflector top bounding surface.
    bottom_reflector_boundary : openmc.ZPlane
        Reflector bottom bounding surface.
    hast : openmc.Material
        Hastelloy-N material

    Returns
    -------
    c1 : openmc.Cell
        Radial vessel wall.
    c2 : openmc.Cell
        Bottom vessel wall.
    c3 : openmc.Cell
        Top vessel wall.
    """
    radial_vessel_reg = (+radial_reflector_boundary &
                         -radial_vessel_boundary &
                         -top_vessel_boundary &
                         +bottom_vessel_boundary)
    bottom_vessel_reg = (-radial_reflector_boundary &
                         -bottom_reflector_boundary &
                         +bottom_vessel_boundary)
    top_vessel_reg = (-radial_reflector_boundary &
                      -top_vessel_boundary &
                      +top_reflector_boundary)

    c1 = openmc.Cell(fill=hast, region=radial_vessel_reg,
                     name='radial_vessel_wall')
    c2 = openmc.Cell(fill=hast, region=bottom_vessel_reg,
                     name='bottom_vessel_wall')
    c3 = openmc.Cell(fill=hast, region=top_vessel_reg,
                     name='top_vessel_wall')
    return c1, c2, c3
