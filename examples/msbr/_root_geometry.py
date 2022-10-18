import openmc
import numpy as np

def shared_root_geometry():
    cr_boundary = openmc.model.rectangular_prism(15.24*2, 15.24*2)
    core_base = openmc.ZPlane(z0=0.0, name='core_base')
    core_top = openmc.ZPlane(z0=449.58, name='core_top')

    s1 = openmc.model.IsogonalOctagon(center=(0.0,0.0), r1=208.28, r2=222.71, name='base_octader')
    s2 = openmc.model.IsogonalOctagon(center=(0.0,0.0), r1=218.44, r2=215.53, name='smaller_octader')
    s3 = openmc.model.IsogonalOctagon(center=(0.0,0.0), r1=228.60, r2=193.97, name='smallest_octader')
    zone_i_boundary = -s1 | -s2 | -s3

    zone_ii_boundary = openmc.ZCylinder(r=256.032, name='iib_boundary')
    annulus_boundary = openmc.ZCylinder(r=261.112, name='annulus_boundary')
    lower_plenum_boundary = openmc.ZPlane(z0=-7.62, name='lower_plenum_boundary')

    zone_bounds = (cr_boundary, zone_i_boundary, zone_ii_boundary)
    core_bounds = (annulus_boundary, lower_plenum_boundary, core_base, core_top)
    radial_reflector_boundary = openmc.ZCylinder(r=338.328, name='radial_reflector_boundary')
    bottom_reflector_boundary = openmc.ZPlane(z0=-76.2, name='bottom_axial_reflector_boundary')
    top_reflector_boundary = openmc.ZPlane(z0=525.78, name='top_axial_reflector_boundary')
    reflector_bounds = (radial_reflector_boundary,
                        bottom_reflector_boundary,
                        top_reflector_boundary)

    radial_vessel_boundary = openmc.ZCylinder(r=343.408, name='radial_vessel_wall', boundary_type='vacuum')
    bottom_vessel_boundary = openmc.ZPlane(z0=-81.28, name='bottom_vessel_wall', boundary_type='vacuum')
    top_vessel_boundary = openmc.ZPlane(z0=530.86, name='top_vessel_wall', boundary_type='vacuum')

    vessel_bounds = (radial_vessel_boundary,
                     bottom_vessel_boundary,
                     top_vessel_boundary)

    return zone_bounds, core_bounds, reflector_bounds, vessel_bounds

def zoneIIB(zone_i_boundary, zone_ii_boundary, annulus_boundary, core_base, core_top, moder, fuel):
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

    hole_coord = 242.679
    hole_region = +openmc.ZCylinder(x0=hole_coord, r=3.0875)

    # Small elements
    small_angular_width = 0.96
    adjacent_angular_offset = 0.675 #27/40
    small_elems_per_octant = 25

    zone_iib_reg = None
    elem_cells = []
    for i, pos in enumerate(large_positions):
        pos = np.round(pos, 3)
        r1, r2 = big_radii[i]
        t1 = pos - large_half_w
        t2 = pos + large_half_w
        large_elem = openmc.model.CylinderSector(r1, r2, t1, t2)
        elem_hole = hole_region.rotate((0.0, 0.0, pos))
        elem_reg = -large_elem
        if isinstance(zone_iib_reg, openmc.Region):
            zone_iib_reg = zone_iib_reg | elem_reg
        else:
            zone_iib_reg = elem_reg

        elem_reg = -large_elem & elem_hole
        elem_cells.append(openmc.Cell(fill=moder, region=elem_reg,
                                      name=f'iib_large_element_moderator_{pos}'))
        elem_cells.append(openmc.Cell(fill=fuel, region=~elem_hole,
                                      name=f'iib_large_element_fuel_hole_{pos}'))
        t1 = t2 + adjacent_angular_offset
        r1, r2 = small_radii
        for i in range(0, small_elems_per_octant):
            t2 = t1 + small_angular_width
            elem_reg = -openmc.model.CylinderSector(small_radii[0], small_radii[1], t1, t2)
            pos = t2 - (small_angular_width / 2)
            pos = np.round(pos, 3)
            elem_cells.append(openmc.Cell(fill=moder, region=elem_reg, name=f'iib_small_element_{pos}'))
            zone_iib_reg = zone_iib_reg | elem_reg
            t1 = t2 + adjacent_angular_offset
    c1 = openmc.Cell(fill=fuel, region=(~zone_iib_reg &
                                        ~zone_i_boundary &
                                        -zone_ii_boundary &
                                        +core_base &
                                        -core_top), name='iib_fuel')

    iib = openmc.Universe(name='zone_iib')
    iib.add_cells(elem_cells)
    iib.add_cell(c1)

    iib = openmc.Cell(fill=iib, region=(~zone_i_boundary &
                                        -zone_ii_boundary &
                                        +core_base &
                                        -core_top), name='zone_iib')
    return iib

def annulus(zone_ii_boundary, annulus_boundary, core_base, core_top, fuel):
    annulus_reg = +zone_ii_boundary & -annulus_boundary & +core_base & -core_top
    c1 = openmc.Cell(fill=fuel, region=annulus_reg, name='annulus')
    return c1

def lower_plenum(core_base, lower_plenum_boundary, annulus_boundary, fuel):
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
    radial_reflector_reg = +annulus_boundary & -radial_reflector_boundary & +bottom_reflector_boundary & -top_reflector_boundary
    bottom_reflector_reg = -annulus_boundary & -lower_plenum_boundary & +bottom_reflector_boundary
    top_reflector_reg = -annulus_boundary & +core_top & -top_reflector_boundary

    c1 = openmc.Cell(fill=moder, region=radial_reflector_reg, name='radial_reflector')
    c2 = openmc.Cell(fill=moder, region=bottom_reflector_reg, name='bottom_axial_reflector')
    c3 = openmc.Cell(fill=moder, region=top_reflector_reg, name='top_axial_reflector')
    return c1, c2, c3

def vessel(radial_reflector_boundary,
           radial_vessel_boundary,
           bottom_vessel_boundary,
           top_vessel_boundary,
           top_reflector_boundary,
           bottom_reflector_boundary,
           hast):
    radial_vessel_reg = +radial_reflector_boundary & -radial_vessel_boundary & -top_vessel_boundary & +bottom_vessel_boundary
    bottom_vessel_reg = -radial_reflector_boundary & -bottom_reflector_boundary & +bottom_vessel_boundary
    top_vessel_reg = -radial_reflector_boundary & -top_vessel_boundary & +top_reflector_boundary

    c1 = openmc.Cell(fill=hast, region=radial_vessel_reg, name='radial_vessel_wall')
    c2 = openmc.Cell(fill=hast, region=bottom_vessel_reg, name='bottom_vessel_wall')
    c3 = openmc.Cell(fill=hast, region=top_vessel_reg, name='top_vessel_wall')
    return c1, c2, c3
