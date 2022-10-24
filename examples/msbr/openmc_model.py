import openmc
import numpy as np
import argparse

from openmc.deplete import CoupledOperator, PredictorIntegrator, CELIIntegrator

from _core_elements import *
from _control_rods import *
from _root_geometry import *

# Materials

fuel = openmc.Material(name='fuel')
fuel.set_density('g/cm3', density=3.35)
fuel.add_components({'Li7': 0.0787474673879085,
                     'Be9': 0.0225566879138321,
                     'F19': 0.454003012179284,
                     'Th232': 0.435579130482336,
                     'U233': 0.00911370203663893},
                    percent_type='wo')
fuel.depletable = True
fuel.volume = 48710000.0

moder = openmc.Material(name='graphite')
moder.set_density('g/cm3', density=1.84)
moder.add_nuclide('C0', 1.000, percent_type='wo')
moder.add_s_alpha_beta('c_Graphite')

hast = openmc.Material(name='hastelloyN')
hast.set_density('g/cm3', density=8.671)
hast.add_components({'Al27': 0.003,
                     'Ni': 0.677,
                     'W': 0.250,
                     'Cr': 0.070},
                    percent_type='wo')

mat = openmc.Materials(materials=[fuel, moder, hast])
mat.export_to_xml()

def parse_arguments():
    """Parses arguments from command line.

    Parameters
    ----------

    Returns
    -------

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--optimized',
                        type=bool,
                        default=False,
                        help='flag to generate model \
                        with only simple regions')
    parser.add_argument('--deplete',
                        type=bool,
                        default=False,
                        help='flag for running depletion')

    args = parser.parse_args()
    return bool(args.optimized), bool(args.deplete)

def shared_elem_geometry(elem_type, eb_d, gr_sq_d, gr_sq_r, r_dt, l1, l2, l3, r_es, es_name, optimized):
    """Surfaces and regions shared by Zone IA and Zone IIA elements.
    Specs found in Robertson, 1971 Fig 3.4 (p. 17) and Fig 3.5 (p.18)"""
    elem_bound = openmc.rectangular_prism(eb_d*2, eb_d*2) # Pin outer boundary
    gr_sq_neg = openmc.rectangular_prism(gr_sq_d*2, gr_sq_d*2, corner_radius=gr_sq_r) # Graphite square

    ul_t = openmc.ZCylinder(-l1, -l3, r_dt, name='corner_ul_tip')
    br_t = openmc.ZCylinder(l1, l3, r_dt, name='corner_br_tip')
    ru_t = openmc.ZCylinder(-l3, l1, r_dt, name='corner_ru_tip')
    lb_t = openmc.ZCylinder(l3, -l1, r_dt, name='corner_lb_tip')

    if optimized:
        eb_minx, eb_maxx, eb_miny, eb_maxy = list(elem_bound.get_surfaces().values())

        gr_sq_neg = openmc.rectangular_prism(gr_sq_d*2, gr_sq_d*2, corner_radius=gr_sq_r) # Graphite square
        (gr_minx, gr_maxx, gr_miny, gr_maxy,
        gr_cyl_lb, gr_cyl_minx, gr_cyl_miny,
        gr_cyl_ul, gr_cyl_maxy, gr_cyl_br,
        gr_cyl_maxx, gr_cyl_ru) = list(gr_sq_neg.get_surfaces().values())

        # remaining square
        gr_sq_neg = +gr_minx & -gr_maxx & +gr_cyl_miny & -gr_cyl_maxy

    # create separating rod tip regions
    gr_ul_t = -ul_t
    gr_br_t = -br_t
    gr_ru_t = -ru_t
    gr_lb_t = -lb_t

    if elem_type == 'core':
        # for main pin section for both I-A and II-A
        ul = openmc.ZCylinder(-l1, l2, r_dt, name='corner_ul')
        br = openmc.ZCylinder(l1, -l2, r_dt, name='corner_br')
        lb = openmc.ZCylinder(-l2, -l1, r_dt, name='corner_lb')
        ru = openmc.ZCylinder(l2, l1, r_dt, name='corner_ru')

        if optimized:
            # corner regions
            gr_ul = -ul & +gr_maxy
            gr_ul_fill = -ul & +gr_cyl_ul & -gr_maxy & -gr_cyl_minx & +gr_cyl_maxy
            gr_br = -br & -gr_miny
            gr_br_fill = -br & +gr_cyl_br & +gr_miny & +gr_cyl_maxx & -gr_cyl_miny
            gr_lb = -lb & -gr_minx
            gr_lb_fill = -lb & +gr_cyl_lb & +gr_minx & -gr_cyl_minx & -gr_cyl_miny
            gr_ru = -ru & +gr_maxx
            gr_ru_fill = -ru & +gr_cyl_ru & -gr_maxx & +gr_cyl_maxx & +gr_cyl_maxy

            # inter-element channel regions
            iec_r = +gr_cyl_miny & -gr_cyl_maxy & +gr_maxx & +lb_t & +ru & +gr_cyl_ru
            iec_ru = (+gr_cyl_ru & +gr_cyl_maxx & +gr_cyl_maxy) & +ru & +br_t
            iec_u = +gr_cyl_minx & -gr_cyl_maxx & +gr_maxy & +br_t & +ul & +gr_cyl_ul
            iec_ul = (+gr_cyl_ul & -gr_cyl_minx & +gr_cyl_maxy) & +ul & +ru_t
            iec_l = +gr_cyl_miny & -gr_cyl_maxy & -gr_minx & +ru_t & +lb & +gr_cyl_lb
            iec_lb = (+gr_cyl_lb & -gr_cyl_minx & -gr_cyl_miny) & +lb & +ul_t
            iec_b = +gr_cyl_minx & -gr_cyl_maxx & -gr_miny & +ul_t & +br & +gr_cyl_br
            iec_br = (+gr_cyl_br & +gr_cyl_maxx & -gr_cyl_miny) & +br & +lb_t

            inter_elem_channel = [[iec_r, 'outer_r'], [iec_ru, 'outer_ru'],
                                  [iec_u, 'outer_u'], [iec_ul, 'outer_ul'],
                                  [iec_l, 'outer_l'], [iec_lb, 'outer_lb'],
                                  [iec_b, 'outer_b'], [iec_br, 'outer_br']]
        else:
            gr_ul = -ul
            gr_br = -br
            gr_lb = -lb
            gr_ru = -ru

            inter_elem_channel = +ul & +br & +lb & +ru

    elif elem_type == 'cr':
        # params for control rods
        r_d = 1.16
        e_d = 2 * r_d / np.sqrt(3)
        r_c = 0.18

        ul = openmc.model.hexagonal_prism(origin=(-l1, l2), edge_length=e_d, orientation='x', corner_radius=r_c)
        br = openmc.model.hexagonal_prism(origin=(l1, -l2), edge_length=e_d, orientation='x',corner_radius=r_c)
        lb = openmc.model.hexagonal_prism(origin=(-l2, -l1), edge_length=e_d, orientation='y',corner_radius=r_c)
        ru = openmc.model.hexagonal_prism(origin=(l2, l1), edge_length=e_d, orientation='y',corner_radius=r_c)

        if optimized:
            (ul_u, ul_b, ul_ur, ul_br, ul_bl, ul_ul,
             ul_cyl_bl_in, ul_cyl_bl_out,
             ul_cyl_ul_in, ul_cyl_ul_out,
             ul_cyl_br_in, ul_cyl_br_out,
             ul_cyl_ur_in, ul_cyl_ur_out,
             ul_cyl_l_in, ul_cyl_l_out,
             ul_cyl_r_in, ul_cyl_r_out)= list(ul.get_surfaces().values())
            (br_u, br_b, br_ur, br_br, br_bl, br_ul,
             br_cyl_bl_in, br_cyl_bl_out,
             br_cyl_ul_in, br_cyl_ul_out,
             br_cyl_br_in, br_cyl_br_out,
             br_cyl_ur_in, br_cyl_ur_out,
             br_cyl_l_in, br_cyl_l_out,
             br_cyl_r_in, br_cyl_r_out)= list(br.get_surfaces().values())
            (lb_r, lb_l, lb_ur, lb_ul, lb_br, lb_bl,
             lb_cyl_lb_in, lb_cyl_lb_out,
             lb_cyl_lu_in, lb_cyl_lu_out,
             lb_cyl_rb_in, lb_cyl_rb_out,
             lb_cyl_ru_in, lb_cyl_ru_out,
             lb_cyl_b_in, lb_cyl_b_out,
             lb_cyl_u_in, lb_cyl_u_out)= list(lb.get_surfaces().values())
            (ru_r, ru_l, ru_ur, ru_ul, ru_br, ru_bl,
             ru_cyl_lb_in, ru_cyl_lb_out,
             ru_cyl_lu_in, ru_cyl_lu_out,
             ru_cyl_rb_in, ru_cyl_rb_out,
             ru_cyl_ru_in, ru_cyl_ru_out,
             ru_cyl_b_in, ru_cyl_b_out,
             ru_cyl_u_in, ru_cyl_u_out)= list(ru.get_surfaces().values())

            # corner regions
            gr_ul = -ul_ul & -ul_ur & +gr_maxy
            gr_ul_fill = -ul_ul & +ul_bl & +ul_cyl_l_out & +gr_cyl_ul & -gr_maxy & -gr_cyl_minx & +gr_cyl_maxy
            gr_lb = +lb_bl & -lb_ul & -gr_minx
            gr_lb_fill = +lb_bl & +lb_br & +lb_cyl_b_out & +gr_cyl_lb & +gr_minx & -gr_cyl_miny & -gr_cyl_minx
            gr_br = +br_br & +br_bl & -gr_miny
            gr_br_fill = +br_br & -br_ur & +br_cyl_r_out & +gr_cyl_br & +gr_miny & +gr_cyl_maxx & -gr_cyl_miny
            gr_ru = +ru_br & -ru_ur & +gr_maxx
            gr_ru_fill = -ru_ur & -ru_ul & +ru_cyl_u_out & +gr_cyl_ru & -gr_maxx & +gr_cyl_maxy & +gr_cyl_maxx

            # inter-element channel regions
            iec_r = +gr_cyl_miny & +gr_maxx & +lb_t & -ru_br
            iec_ru_main = +gr_cyl_ru & (+ru_ur) & +br_t
            iec_ru_fill1 = +gr_cyl_ru & +gr_cyl_maxx & (+ru_ul & -ru_ur) & +br_t
            iec_ru_fill2 = +gr_cyl_ru & ((-ru_cyl_u_out)) & -ru_ul & -ru_ur
            iec_u = -gr_cyl_maxx & +gr_maxy & +br_t & +ul_ur
            iec_ul_main = +gr_cyl_ul & (+ul_ul) & +ru_t
            iec_ul_fill1 = +gr_cyl_ul & +gr_cyl_maxy & (-ul_bl & -ul_ul) & +ru_t
            iec_ul_fill2 = +gr_cyl_ul & ((-ul_cyl_l_out)) & +ul_bl & -ul_ul
            iec_l = -gr_cyl_maxy & -gr_minx & +ru_t & +lb_ul
            iec_lb_main = +gr_cyl_lb & (-lb_bl) & +ul_t
            iec_lb_fill1 = +gr_cyl_lb & -gr_cyl_minx & (-lb_br & +lb_bl) & +ul_t
            iec_lb_fill2 = +gr_cyl_lb & ((-lb_cyl_b_out)) & +lb_br & +lb_bl
            iec_b = +gr_cyl_minx & -gr_miny & +ul_t & -br_bl
            iec_br_main = +gr_cyl_br & (-br_br) & +lb_t
            iec_br_fill1 = +gr_cyl_br & -gr_cyl_miny & (+br_ur & +br_br) & +lb_t
            iec_br_fill2 = +gr_cyl_br & ((-br_cyl_r_out)) & -br_ur & +br_br
            inter_elem_channel = [[iec_r, 'outer_r'], [iec_ru_main, 'outer_ru_main'],
                                  [iec_ru_fill1, 'outer_ru_fill1'], [iec_ru_fill2, 'outer_ru_fill2'],
                                  [iec_u, 'outer_u'], [iec_ul_main, 'outer_ul_main'],
                                  [iec_ul_fill1, 'outer_ul_fill1'], [iec_ul_fill2, 'outer_ul_fill2'],
                                  [iec_l, 'outer_l'], [iec_lb_main, 'outer_lb_main'],
                                  [iec_lb_fill1, 'outer_lb_fill1'], [iec_lb_fill2, 'outer_lb_fill2'],
                                  [iec_b, 'outer_b'], [iec_br_main, 'outer_br_main'],
                                  [iec_br_fill1, 'outer_br_fill1'], [iec_br_fill2, 'outer_br_fill2']]

        else:
            gr_ul = ul
            gr_lb = br
            gr_br = lb
            gr_ru = ru

            inter_elem_channel = ~ul & ~br & ~lb & ~ru

    gr_corners = [[gr_ul, 'ul'], [gr_br, 'br'],  [gr_ru, 'ru'], [gr_lb, 'lb'],
                  [gr_ul_t, 'ul_t'], [gr_br_t, 'br_t'], [gr_ru_t, 'ru_t'], [gr_lb_t, 'lb_t']]

    if optimized:
        gr_corners += [[gr_ul_fill, 'ul_fill'], [gr_br_fill, 'br_fill'], [gr_ru_fill, 'ru_fill'], [gr_lb_fill, 'lb_fill']]

        # slabs that line up with rounded edges
        slab_u = -gr_maxy & +gr_cyl_maxy & -gr_cyl_maxx & +gr_cyl_minx
        #slab_l = +gr_minx & -gr_cyl_minx & -gr_cyl_maxy & +gr_cyl_miny
        slab_b = +gr_miny & -gr_cyl_miny & -gr_cyl_maxx & +gr_cyl_minx
        #slab_r = -gr_maxx & +gr_cyl_maxx & -gr_cyl_maxy & +gr_cyl_miny
        slabs = [[slab_u, 'slab_u'],
                 #[slab_l, 'slab_l'],
                 [slab_b, 'slab_b']]
                 #[slab_r, 'slab_r']]

        # the rounded edges themselves
        quarter_ul = -gr_cyl_ul & -gr_cyl_minx & +gr_cyl_maxy
        quarter_br = -gr_cyl_br & +gr_cyl_maxx & -gr_cyl_miny
        quarter_lb = -gr_cyl_lb & -gr_cyl_minx & -gr_cyl_miny
        quarter_ru = -gr_cyl_ru & +gr_cyl_maxx & +gr_cyl_maxy
        quarters = [[quarter_ul, 'quarter_ul'], [quarter_br, 'quarter_br'],  [quarter_ru, 'quarter_ru'], [quarter_lb, 'quarter_lb']]

        gr_corners= slabs + quarters + gr_corners
    else:
        inter_elem_channel = inter_elem_channel & +ul_t & +br_t & +ru_t & +lb_t


    extra_surf = openmc.ZCylinder(r=r_es, name=es_name)


    return elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, extra_surf

def cr_lattice(cr_boundary, core_base, core_top, optimized):
    elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, fuel_hole = shared_elem_geometry('cr', 7.62, 7.23645, 0.99, 0.8, 5.8801, 6.505, 8.03646, 5.08, 'cr_fuel_hole', optimized)

    f = control_rod(elem_bound, gr_sq_neg, gr_corners,inter_elem_channel, fuel_hole, fuel, moder, optimized)
    if optimized:
        # call a second time to have unique surfaces
        elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, fuel_hole = shared_elem_geometry('cr', 7.62, 7.23645, 0.99, 0.8, 5.8801, 6.505, 8.03646, 5.08, 'cr_fuel_hole', optimized)
    e = control_rod_channel(elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, fuel_hole, fuel, moder, optimized)

    cr = openmc.RectLattice()
    cr.pitch = np.array([15.24, 15.24])
    N = 2 / 2
    cr.lower_left = -1 * cr.pitch * N
    cr.universes = [[f, e],
                    [e, f]]
    c1 = openmc.Cell(fill=cr, region=(+core_base & -core_top & cr_boundary), name='cr_lattice')

    return c1

def main_lattice(zone_i_boundary, cr_boundary, core_base, core_top, optimized):
    elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, gr_round_4 = shared_elem_geometry('core', 5.08, 4.953, 0.46, 0.66802, 4.28498, 4.53898, 5.62102, 2.2225, 'gr_round_4', optimized)
    l = zoneIA(elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, gr_round_4, moder, fuel, hast, optimized)
    elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, gr_round_4 = shared_elem_geometry('core', 5.08, 4.953, 0.46, 0.66802, 4.28498, 4.53898, 5.62102, 2.2225, 'gr_round_4', optimized)
    z = zoneIIA(elem_bound, gr_sq_neg, gr_corners, inter_elem_channel, gr_round_4, moder, fuel, optimized)
    v = void_cell(elem_bound, optimized)
    # tres, uno, dos, quatro
    t, u, d, q = graphite_triangles(elem_bound, moder, fuel, optimized)

    s1, s2, s3 = zone_i_boundary

    main = openmc.RectLattice()
    main.pitch = np.array([10.16, 10.16])
    N = 45 / 2
    main.lower_left = -1 * main.pitch * N
    main.universes = [[v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, d, z, z, z, z, z, z, z, z, z, u, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, v, v, v, d, z, z, z, z, l, l, l, l, l, l, l, l, l, z, z, z, z, u, v, v, v, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, v, d, z, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, z, u, v, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v, v, v],
                      [v, v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v, v],
                      [v, v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v, v],
                      [v, v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v, v],
                      [v, v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v, v],
                      [v, v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v, v],
                      [v, d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u, v],
                      [v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v],
                      [v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v],
                      [v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v],
                      [d, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, u],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, v, v, v, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, v, v, v, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, v, v, v, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z],
                      [t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q],
                      [v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v],
                      [v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v],
                      [v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v],
                      [v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v],
                      [v, v, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, v, v],
                      [v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v],
                      [v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v],
                      [v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v],
                      [v, v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v, v],
                      [v, v, v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, t, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, q, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, v, t, z, z, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, z, z, q, v, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, v, v, v, t, z, z, z, z, l, l, l, l, l, l, l, l, l, z, z, z, z, q, v, v, v, v, v, v, v, v, v, v, v, v, v],
                      [v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, t, z, z, z, z, z, z, z, z, z, q, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v]]
    if optimized:
        # Octagon subsurfaces
        oct1_maxy, oct1_miny, oct1_maxx, oct1_minx, oct1_ur, oct1_br, oct1_bl, oct1_ul = list((-s1).get_surfaces().values())
        oct2_maxy, oct2_miny, oct2_maxx, oct2_minx, oct2_ur, oct2_br, oct2_bl, oct2_ul = list((-s2).get_surfaces().values())
        oct3_maxy, oct3_miny, oct3_maxx, oct3_minx, oct3_ur, oct3_br, oct3_bl, oct3_ul = list((-s3).get_surfaces().values())
        cb_minx, cb_maxx, cb_miny, cb_maxy = list(cr_boundary.get_surfaces().values())

        c1_ur = (-oct3_ur & +oct2_ur & -oct2_maxx & -oct2_maxy)
        c1_ul = (+oct3_ul & -oct2_ul & +oct2_minx & -oct2_maxy)
        c1_bl = (+oct3_bl & -oct2_bl & +oct2_minx & +oct2_miny)
        c1_br = (-oct3_br & +oct2_br & -oct2_maxx & +oct2_miny)
        c1 = [[c1_ur, 'smaller_octader_ur'],
              [c1_ul, 'smaller_octader_ul'],
              [c1_bl, 'smaller_octader_bl'],
              [c1_br, 'smaller_octader_br']]

        c2_r = (+cb_maxx & +cb_miny & -cb_maxy & -oct3_maxx)
        c2_ur = (+cb_maxx & +cb_maxy & -oct3_maxx & -oct3_maxy & +oct3_ur)
        c2_u = (+cb_maxy & +cb_minx & -cb_maxx & -oct3_maxy)
        c2_ul = (-cb_minx & +cb_maxy & +oct3_minx & -oct3_maxy & -oct3_ul)
        c2_l = (-cb_minx & +cb_miny & -cb_maxy & +oct3_minx)
        c2_bl = (-cb_minx & -cb_miny & +oct3_minx & +oct3_miny & -oct3_bl)
        c2_b = (-cb_miny & +cb_minx & -cb_maxx & +oct3_miny)
        c2_br = (+cb_maxx & -cb_miny & -oct3_maxx & +oct3_miny & +oct3_br)
        c2 = [[c2_r, 'smallest_octader_r'],
              [c2_ur, 'smallest_octader_ur'],
              [c2_u, 'smallest_octader_u'],
              [c2_ul, 'smallest_octader_ul'],
              [c2_l, 'smallest_octader_l'],
              [c2_bl, 'smallest_octader_bl'],
              [c2_b, 'smallest_octader_b'],
              [c2_br, 'smallest_octader_br']]
        #c2 = [[-s3, 'smallest_octader']]

        c3_ur = (-oct2_ur & +oct1_ur & -oct1_maxx & -oct1_maxy)
        c3_ul = (+oct2_ul & -oct1_ul & +oct1_minx & -oct1_maxy)
        c3_bl = (+oct2_bl & -oct1_bl & +oct1_minx & +oct1_miny)
        c3_br = (-oct2_br & +oct1_br & -oct1_maxx & +oct1_miny)
        c3 = [[c3_ur, 'base_octader_ur'],
              [c3_ul, 'base_octader_ul'],
              [c3_bl, 'base_octader_bl'],
              [c3_br, 'base_octader_br']]

        regs = c1 + c2 + c3
        main_cells = []
        for reg, name in regs:
            main_cells.append(openmc.Cell(fill=main, region=(reg & +core_base & -core_top), name=name))

    else:
        c1 = openmc.Cell(fill=main, region=(+core_base & -core_top &
                                            +zone_i_boundary[2] & -zone_i_boundary[1] &
                                            ~cr_boundary), name='main_lattice_smaller_octader')
        c2 = openmc.Cell(fill=main, region=(+core_base & -core_top &
                                            -zone_i_boundary[2] &
                                            ~cr_boundary), name='main_lattice_insite_smallest_octader')
        c3 = openmc.Cell(fill=main, region=(+core_base & -core_top &
                                            -zone_i_boundary[0] & +zone_i_boundary[1] & +zone_i_boundary[2] &
                                            ~cr_boundary), name='main_lattice_inside_base_octader_deducted_smaller_smallest')
        main_cells = [c1, c2, c3]
    return main_cells

optimized, deplete = parse_arguments()
zone_bounds, core_bounds, reflector_bounds, vessel_bounds = shared_root_geometry()

cr_boundary, zone_i_boundary, zone_ii_boundary = zone_bounds
annulus_boundary, lower_plenum_boundary, core_base, core_top = core_bounds
radial_reflector_boundary, bottom_reflector_boundary, top_reflector_boundary = reflector_bounds
radial_vessel_boundary, bottom_vessel_boundary, top_vessel_boundary= vessel_bounds

main = main_lattice(zone_i_boundary, cr_boundary, core_base, core_top, optimized)
cr = cr_lattice(cr_boundary, core_base, core_top, optimized)
iib = zoneIIB(zone_i_boundary, zone_ii_boundary, annulus_boundary, core_base, core_top, moder, fuel, optimized)
a = annulus(zone_ii_boundary, annulus_boundary, core_base, core_top, fuel)
lp = lower_plenum(core_base, lower_plenum_boundary, annulus_boundary, fuel)

rr, rb, rt = reflectors(annulus_boundary,
               radial_reflector_boundary,
               lower_plenum_boundary,
               bottom_reflector_boundary,
               core_top,
               top_reflector_boundary,
               moder)

vr, vb, vt = vessel(radial_reflector_boundary,
           radial_vessel_boundary,
           bottom_vessel_boundary,
           top_vessel_boundary,
           top_reflector_boundary,
           bottom_reflector_boundary,
           hast)

geo = openmc.Geometry()
univ = openmc.Universe(cells=[cr, lp, a, rr, rb, rt, vr, vb, vt])
univ.add_cells(main)
univ.add_cells(iib)

geo.root_universe = univ
geo.remove_redundant_surfaces()
geo.export_to_xml()

# Settings
settings = openmc.Settings()
settings.particles = 10000
settings.batches = 150
settings.inactive = 25
settings.temperature = {'default': 900, 'method': 'interpolation', 'range': (800, 1000)}
settings.export_to_xml()

# Plots
plots_3d = False
detail_pixels = (1000, 1000)
full_pixels = (10000, 10000)

colormap = {moder: 'purple',
            hast: 'blue',
            fuel: 'yellow'}
## Slice plots
plots = openmc.Plots()

plot = openmc.Plot(name='serpent-plot1')
plot.origin=(0., 0., 150.5)
plot.pixels=full_pixels
plot.width=(686.816, 686.816)
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='serpent-plot1')
plot.origin=(0.0, -77.5, 306.07)
plot.pixels=(1550, 3400)
plot.width=(155, 612.14)
plot.color_by='material'
plot.colors=colormap
plot.basis='yz'
plots.append(plot)

plot = openmc.Plot(name='serpent-plot2')
plot.origin=(0, 0, 155)
plot.pixels=(1000, 1000)
plot.width=(40, 40)
plot.color_by='material'
plot.colors=colormap
plot.basis='yz'
plots.append(plot)

plot = openmc.Plot(name='serpent-plot3')
plot.origin=(16.5, 0, 306.07)
plot.pixels=(2000, 2000)
plot.width=(686.816, 612.14)
plot.color_by='material'
plot.colors=colormap
plot.basis='yz'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIA-IIA-lower1')
plot.origin=(215, 0, 10.0)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIA-main')
plot.origin=(215, 0, 23.0)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIIA-upper1')
plot.origin=(215, 0, 435)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIA-upper1')
plot.origin=(215, 0, 420)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIIA-upper2')
plot.origin=(215, 0, 437)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIA-upper2')
plot.origin=(215, 0, 439)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIIA-upper3')
plot.origin=(215, 0, 440)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIA-upper3')
plot.origin=(215, 0, 448)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='detail-zoneIIA-upper4')
plot.origin=(215, 0, 442)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-IIA-lower1')
plot.origin=(0.0, 0, 10.0)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-main')
plot.origin=(0, 0, 23.0)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper1')
plot.origin=(0, 0, 435)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-upper1')
plot.origin=(0, 0, 420)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper2')
plot.origin=(0, 0, 437)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-upper2')
plot.origin=(0, 0, 439)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper3')
plot.origin=(0, 0, 440)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-upper3')
plot.origin=(0, 0, 448)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper4')
plot.origin=(0, 0, 442)
plot.width=(522.232, 522.232)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='core-xz-detail-upper')
plot.origin=(215, 0, 440)
plot.width=(100, 100)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xz'
plots.append(plot)

plot = openmc.Plot(name='full-core-xz')
plot.origin=(0, 0, 306.07)
plot.width = (686.816, 612.14)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xz'
plots.append(plot)

if plots_3d:
    plot = openmc.Plot(name='full-core-3d')
    plot.origin=(0,0,220)
    plot.type = 'voxel'
    plot.color_by='materials'
    plot.colors=colormap
    plot.width = (700., 700., 650.)
    plot.pixels = (10000, 10000, 10000)

    plots.append(plot)

plots.export_to_xml()

if deplete:
    fiss_q = {
        "Am243": 212952778.98135212,
        "Cm246": 220179493.9541502,
        "U239": 196182721.4907133,
        "Np239": 198519429.0542043,
        "Th233": 185840570.73897627,
        "Cf251": 223166396.6983342,
        "Am242": 215146730.16368726,
        "Cm245": 214624022.18345505,
        "Cf254": 230600814.3619568,
        "Am241": 211216798.63643932,
        "Th232": 197108389.42449385,
        "Cm240": 219583368.40646642,
        "Th231": 186918512.14598972,
        "Bk246": 224446497.874413,
        "Cm247": 218956599.9139631,
        "U238": 206851381.70909396,
        "Bk250": 225432928.78068554,
        "U230": 198841127.68309468,
        "Cf249": 221434495.10716867,
        "U234": 200632850.9958874,
        "Cm250": 219425761.1783332,
        "Th229": 192235847.44789958,
        "Cm241": 219075406.6897822,
        "Pu237": 210593272.23024797,
        "Am240": 215272544.02927735,
        "Cm249": 218622037.52325428,
        "Ac226": 183632605.3770991,
        "Cf250": 229685291.02082983,
        "Th228": 189488754.50737157,
        "Cf248": 229015120.40511796,
        "Ac227": 183458264.80025893,
        "Pu241": 211237715.32232296,
        "Pu240": 208612566.66049656,
        "Cf252": 230239896.94703457,
        "U231": 197643438.24939737,
        "Cm242": 212786491.32857716,
        "Bk245": 225023484.65451327,
        "Np235": 199435370.72904894,
        "Pu243": 207499380.63776916,
        "Pu239": 208018532.78140113,
        "Am242_m1": 215145370.5791048,
        "Pu236": 208679081.72160652,
        "Bk249": 224740691.06136644,
        "Np236": 198952718.20228392,
        "Np234": 200175925.99275926,
        "U237": 196429642.96756968,
        "Cf253": 231148831.53210822,
        "U236": 203404311.87546986,
        "Es254": 232527659.46555784,
        "Ac225": 183891658.531768,
        "Cm243": 213375296.0362017,
        "Bk248": 224456537.88363716,
        "Cm244": 217926766.88448203,
        "Pu242": 212072186.50565082,
        "U241": 198266755.4887299,
        "Np237": 205370480.34853214,
        "Th234": 186385345.82281572,
        "Pa231": 194099942.4938497,
        "Pa230": 194744699.33621296,
        "Pa233": 194162901.71835947,
        "U240": 207137940.30569986,
        "U233": 199796183.56054175,
        "Pu246": 208860847.72193536,
        "Pa232": 193654730.8348164,
        "U232": 193044277.35730234,
        "Am244_m1": 213894761.9301219,
        "Pu244": 208427244.82356748,
        "Np238": 208699370.90691367,
        "Bk247": 224883761.19281054,
        "Am244": 213894761.9301219,
        "Pa229": 194955644.11334947,
        "Cm248": 221723145.3723629,
        "Fm255": 238051756.2074275,
        "Cf246": 229074942.12674516,
        "Th230": 188666101.25156796,
        "Pu238": 209540012.5125772,
        "U235": 202270000.0,
        "Th227": 190640950.14927194
    }
    model = openmc.Model.from_xml()
    op = CoupledOperator(model, chain_file='chain_endfb71_pwr.xml', fission_q=fiss_q)
    timesteps = [3] * 12
    integrator = PredictorIntegrator(op, timesteps, timestep_units='d', power=2.25e9)
    integrator.integrate()
