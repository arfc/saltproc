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
    for i, pos in enumerate(large_positions):
        pos = np.round(pos, 3)
        r1_big, r2_big = big_radii[i]
        t1_big = pos - large_half_w
        t2_big = pos + large_half_w
        s1 = openmc.model.CylinderSector(r1_big, r2_big, t1_big, t2_big)
        s2 = openmc.ZCylinder(**hole_args[i])
        elem_cells.append(openmc.Cell(fill=moder, region=(-s1 & +s2), name=f'iib_large_element_{pos}'))
        elem_cells.append(openmc.Cell(fill=fuel, region=(-s2),
                                      name=f'iib_large_element_fuel_hole_{pos}'))
        t1_small = t2_big + adjacent_angular_offset
        r1_small, r2_small = small_radii

        # Inter element fuel channel
        s3 = openmc.model.CylinderSector(r1_small, r2_small, t2_big, t1_small)
        cpos = t2_big + (adjacent_angular_offset / 2)
        cpos = np.round(cpos, 3)
        elem_cells.append(openmc.Cell(fill=fuel, region=-s3,
                                     name=f'inter_element_fuel_channel_{cpos}'))

        t4a = t1_big - adjacent_angular_offset
        s4 = openmc.model.CylinderSector(r1_small, r1_big, t4a, t1_small)
        elem_cells.append(openmc.Cell(fill=fuel, region=-s4,
                                     name=f'inter_element_fuel_channel_{pos}'))

        for i in range(0, small_elems_per_octant):
            t2_small = t1_small + small_angular_width

            # reflector element
            s5 = openmc.model.CylinderSector(r1_small, r2_small, t1_small, t2_small)
            pos = t2_small - (small_angular_width / 2)
            pos = np.round(pos, 3)
            elem_cells.append(openmc.Cell(fill=moder, region=-s5, name=f'iib_small_element_{pos}'))
            t1_small = t2_small + adjacent_angular_offset

            # inter-element fuel channel
            s6 = openmc.model.CylinderSector(r1_small, r2_small, t2_small, t1_small)
            cpos = t2_small + (adjacent_angular_offset/2)
            cpos = np.round(cpos, 3)
            elem_cells.append(openmc.Cell(fill=fuel, region=-s6,
                                         name=f'inter_element_fuel_channel_{cpos}'))

    #universe_id=10
    iib = openmc.Universe(name='zone_iib')
    iib.add_cells(elem_cells)

    c1 = openmc.Cell(fill=iib, region=(~zone_i_boundary &
                                       -zone_ii_boundary &
                                       +core_base &
                                       -core_top), name='zone_iib')
    return c1

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
