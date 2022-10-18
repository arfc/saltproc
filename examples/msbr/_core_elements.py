import openmc
import numpy as np

def _bound_zone_cells(cells_tuples, levels):
    """Helper function that moves Zone IA and Zone IIA cells to the
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

def shared_elem_geometry():
    """Surfaces and regions shared by Zone IA and Zone IIA elements.
    Specs found in Robertson, 1971 Fig 3.4 (p. 17) and Fig 3.5 (p.18)"""

    elem_bound = openmc.rectangular_prism(5.08*2, 5.08*2) # Pin outer boundary
    eb_minx, eb_maxx, eb_miny, eb_maxy = list(elem_bound.get_surfaces().values())

    gr_sq_neg = openmc.rectangular_prism(4.953*2, 4.953*2, corner_radius=0.46) # Graphite square
    (gr_minx, gr_maxx, gr_miny, gr_maxy,
    gr_cyl_lb, gr_cyl_minx, gr_cyl_miny,
    gr_cyl_ul, gr_cyl_maxy, gr_cyl_br,
    gr_cyl_maxx, gr_cyl_ru) = list(gr_sq_neg.get_surfaces().values())

    # params for main pin section for both I-A and II-A
    r_d = 0.66802
    l1 = 4.28498
    l2 = 4.53898
    l3 = 5.62102
    ul = openmc.ZCylinder(-l1, l2, r_d, name='corner_ul')
    br = openmc.ZCylinder(l1, -l2, r_d, name='corner_br')
    lb = openmc.ZCylinder(-l2, -l1, r_d, name='corner_lb')
    ru = openmc.ZCylinder(l2, l1, r_d, name='corner_ru')
    ul_t = openmc.ZCylinder(-l1, -l3, r_d, name='corner_ul_tip')
    br_t = openmc.ZCylinder(l1, l3, r_d, name='corner_br_tip')
    ru_t = openmc.ZCylinder(-l3, l1, r_d, name='corner_ru_tip')
    lb_t = openmc.ZCylinder(l3, -l1, r_d, name='corner_lb_tip')

    gr_ul = -ul & -eb_maxy & +gr_maxy# |
    gr_ul_fill = -ul & +gr_cyl_ul & -gr_maxy & -gr_cyl_minx & +gr_cyl_maxy
    gr_br = -br & +eb_miny & -gr_miny# |
    gr_br_fill = -br & +gr_cyl_br & +gr_miny & +gr_cyl_maxx & -gr_cyl_miny
    gr_lb = -lb & +eb_minx & -gr_minx# |
    gr_lb_fill = -lb & +gr_cyl_lb & +gr_minx & -gr_cyl_minx & -gr_cyl_miny
    gr_ru = -ru & -eb_maxx & +gr_maxx# |
    gr_ru_fill = -ru & +gr_cyl_ru & -gr_maxx & +gr_cyl_maxx & +gr_cyl_maxy

    gr_ul_t = -ul_t & +eb_miny & -gr_miny
    gr_br_t = -br_t & -eb_maxy & +gr_maxy
    gr_ru_t = -ru_t & +eb_minx & -gr_minx
    gr_lb_t = -lb_t & -eb_maxx & +gr_maxx

    gr_corners = (gr_ul, gr_br, gr_lb, gr_ru, gr_ul_fill, gr_br_fill, gr_lb_fill, gr_ru_fill)
    gr_t = (gr_ul_t, gr_br_t, gr_ru_t, gr_lb_t)

    inter_elem_channel = (~gr_sq_neg & elem_bound &
                          +ul & +br & +lb & +ru &
                          +ul_t & +br_t & +ru_t & +lb_t)

    gr_round_4 = openmc.ZCylinder(r=2.2225, name='gr_round_4')

    return elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4

def zoneIA(elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4, moder, fuel, hast):
    """Zone IA element. Specs found in Robertson, 1971 Fig 3.4 (p. 17)"""
    elem_levels = [22.86, 419.10, 438.15, 445.135]
    level_bounds = []
    for level in elem_levels:
        level_bounds.append(openmc.ZPlane(z0=level))
    s1 = openmc.ZCylinder(r=4.953, name='ia_gr_round_1')
    s2 = openmc.ZCylinder(r=1.71069, name='ia_fuel_hole')

    h = 12.66
    theta = np.arctan(4.953 / h)
    r2 = (1 / np.cos(theta))**2 - 1
    s3 = openmc.ZCone(z0=h + elem_levels[2], r2=r2, name='cone_i')

    c1 = openmc.Cell(fill=fuel, region=(-s2), name='ia_fuel_inner_1')
    c2 = openmc.Cell(fill=moder, region=(+s2 & -s1), name='ia_moderator_1')
    c3 = openmc.Cell(fill=fuel, region=(+s1 & elem_bound), name='ia_fuel_outer_1')
    ia1 = (c1, c2, c3)

    # I-A  main (lower 2)
    s2 = s2.clone()
    gr_sq_neg = gr_sq_neg.clone()
    c4 = c1.clone(clone_materials=False)
    c4.name = 'ia_fuel_inner_main'
    c5 = openmc.Cell(fill=moder, region=(+s2 & gr_sq_neg), name='ia_moderator_main')
    c6 = openmc.Cell(fill=fuel, region=(inter_elem_channel), name='ia_fuel_outer_main')
    c5_ul = openmc.Cell(fill=moder, region=gr_corners[0], name='ia_moderator_main_ul')
    c5_br = openmc.Cell(fill=moder, region=gr_corners[1], name='ia_moderator_main_br')
    c5_ru = openmc.Cell(fill=moder, region=gr_corners[2], name='ia_moderator_main_ru')
    c5_lb = openmc.Cell(fill=moder, region=gr_corners[3], name='ia_moderator_main_lb')
    c5_ulf = openmc.Cell(fill=moder, region=gr_corners[4], name='ia_moderator_main_ul_fill')
    c5_brf = openmc.Cell(fill=moder, region=gr_corners[5], name='ia_moderator_main_br_fill')
    c5_ruf = openmc.Cell(fill=moder, region=gr_corners[6], name='ia_moderator_main_ru_fill')
    c5_lbf = openmc.Cell(fill=moder, region=gr_corners[7], name='ia_moderator_main_lb_fill')
    c5_ul_t = openmc.Cell(fill=moder, region=gr_t[0], name='ia_moderator_main_ul_t')
    c5_br_t = openmc.Cell(fill=moder, region=gr_t[1], name='ia_moderator_main_br_t')
    c5_ru_t = openmc.Cell(fill=moder, region=gr_t[2], name='ia_moderator_main_ru_t')
    c5_lb_t = openmc.Cell(fill=moder, region=gr_t[3], name='ia_moderator_main_lb_t')

    iam = (c4, c5, c6,
           c5_ul, c5_br, c5_ru, c5_lb,
           c5_ulf, c5_brf, c5_ruf, c5_lbf,
           c5_ul_t, c5_br_t, c5_ru_t, c5_lb_t)

    # I-A 2 (upper 1)
    c7 = c1.clone(clone_materials=False)
    c7.name = 'ia_fuel_inner_2'
    c8 = c2.clone(clone_materials=False)
    c8.name = 'ia_moderator_2'
    c9 = c3.clone(clone_materials=False)
    c9.name = 'ia_fuel_outer_2'
    ia2 = (c7, c8, c9)

    # I-A 3 (upper 2)'
    s2 = s2.clone()
    s3 = s3.clone()
    elem_bound = elem_bound.clone()
    c10 = c1.clone(clone_materials=False)
    c10.name = 'ia_fuel_inner_3'
    c11 = openmc.Cell(fill=moder, region=(+s2 & -s3), name='ia_moderator_3')
    c12 = openmc.Cell(fill=fuel, region=(+s3 & elem_bound), name='ia_fuel_outer_3')
    ia3 = (c10, c11, c12)

    # I-A 4 (upper 3)
    s2 = s2.clone()
    elem_bound = elem_bound.clone()
    c13 = openmc.Cell(fill=hast, region=(-s2), name='ia_hast')
    c14 = openmc.Cell(fill=moder, region=(+s2 & -gr_round_4), name='ia_moderator_4')
    c15 = openmc.Cell(fill=fuel, region=(+gr_round_4 & elem_bound), name='ia_fuel_outer_4')
    ia4 = (c13, c14, c15)

    elem_cells = [ia1, iam, ia2, ia3, ia4]
    # universe_id=1
    ia = openmc.Universe(name='zone_ia')
    ia.add_cells(_bound_zone_cells(elem_cells, level_bounds))
    return ia

def zoneIIA(elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4, moder, fuel):
    """Zone IIA element. Specs found in Robertson, 1971 Fig 3.5 (p. 18)"""
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
    c2 = openmc.Cell(fill=moder, region=(+s1 & gr_sq_neg), name='iia_moderator_main')
    c3 = openmc.Cell(fill=fuel, region=(inter_elem_channel), name='iia_fuel_outer_main')
    c3.name = 'iia_fuel_outer_main'
    c2_ul = openmc.Cell(fill=moder, region=gr_corners[0], name='iia_moderator_main_ul')
    c2_br = openmc.Cell(fill=moder, region=gr_corners[1], name='iia_moderator_main_br')
    c2_ru = openmc.Cell(fill=moder, region=gr_corners[2], name='iia_moderator_main_ru')
    c2_lb = openmc.Cell(fill=moder, region=gr_corners[3], name='iia_moderator_main_lb')
    c2_ulf = openmc.Cell(fill=moder, region=gr_corners[4], name='iia_moderator_main_ul_fill')
    c2_brf = openmc.Cell(fill=moder, region=gr_corners[5], name='iia_moderator_main_br_fill')
    c2_ruf = openmc.Cell(fill=moder, region=gr_corners[6], name='iia_moderator_main_ru_fill')
    c2_lbf = openmc.Cell(fill=moder, region=gr_corners[7], name='iia_moderator_main_lb_fill')
    c2_ul_t = openmc.Cell(fill=moder, region=gr_t[0], name='iia_moderator_main_ul_t')
    c2_br_t = openmc.Cell(fill=moder, region=gr_t[1], name='iia_moderator_main_br_t')
    c2_ru_t = openmc.Cell(fill=moder, region=gr_t[2], name='iia_moderator_main_ru_t')
    c2_lb_t = openmc.Cell(fill=moder, region=gr_t[3], name='iia_moderator_main_lb_t')
    iiam = (c1, c2, c3, c2_ul, c2_br, c2_ru, c2_lb, c2_ulf, c2_brf, c2_ruf, c2_lbf, c2_ul_t, c2_br_t, c2_ru_t, c2_lb_t)

    # II-A 2 (upper 1)
    gr_sq_neg = gr_sq_neg.clone()
    c4 = openmc.Cell(fill=fuel, region=(-s2), name='iia_fuel_inner_2')
    c5 = openmc.Cell(fill=moder, region=(+s2 & gr_sq_neg), name='iia_moderator_2')
    c6 = c3.clone(clone_materials=False)
    c6.name = 'iia_fuel_outer_2'
    c5_ul = openmc.Cell(fill=moder, region=gr_corners[0], name='iia_moderator_2_ul')
    c5_br = openmc.Cell(fill=moder, region=gr_corners[1], name='iia_moderator_2_br')
    c5_ru = openmc.Cell(fill=moder, region=gr_corners[2], name='iia_moderator_2_ru')
    c5_lb = openmc.Cell(fill=moder, region=gr_corners[3], name='iia_moderator_2_lb')
    c5_ulf = openmc.Cell(fill=moder, region=gr_corners[4], name='iia_moderator_2_ul_fill')
    c5_brf = openmc.Cell(fill=moder, region=gr_corners[5], name='iia_moderator_2_br_fill')
    c5_ruf = openmc.Cell(fill=moder, region=gr_corners[6], name='iia_moderator_2_ru_fill')
    c5_lbf = openmc.Cell(fill=moder, region=gr_corners[7], name='iia_moderator_2_lb_fill')
    c5_ul_t = openmc.Cell(fill=moder, region=gr_t[0], name='iia_moderator_2_ul_t')
    c5_br_t = openmc.Cell(fill=moder, region=gr_t[1], name='iia_moderator_2_br_t')
    c5_ru_t = openmc.Cell(fill=moder, region=gr_t[2], name='iia_moderator_2_ru_t')
    c5_lb_t = openmc.Cell(fill=moder, region=gr_t[3], name='iia_moderator_2_lb_t')
    iia2 = (c4, c5, c6, c5_ul, c5_br, c5_ru, c5_lb, c5_ulf, c5_brf, c5_ruf, c5_lbf, c5_ul_t, c5_br_t, c5_ru_t, c5_lb_t)

    # II-A 3 (upper 2)
    s2 = s2.clone()
    elem_bound = elem_bound.clone()
    c7 = c4.clone(clone_materials=False)
    c7.name = 'iia_fuel_inner_3'
    c8 = openmc.Cell(fill=moder, region=(+s2 & -s3), name='iia_moderator_3')
    c9 = openmc.Cell(fill=fuel, region=(+s3 & elem_bound), name='iia_fuel_outer_3')
    iia3 = (c7, c8, c9)

    # II-A 4 (upper 3)
    elem_bound = elem_bound.clone()
    c10 = openmc.Cell(fill=moder, region=(-s4), name='iia_moderator_4')
    c11 = openmc.Cell(fill=fuel, region=(+s4 & elem_bound), name='iia_fuel_outer_4')
    iia4 = (c10, c11)

    # II-A 5 (upper 4)
    elem_bound = elem_bound.clone()
    c12 = openmc.Cell(fill=moder, region=(-gr_round_4), name='iia_moderator_5')
    c13 = openmc.Cell(fill=fuel, region=(+gr_round_4 & elem_bound), name='iia_fuel_outer_5')
    iia5 = (c12, c13)

    elem_cells = [iiam, iia2, iia3, iia4, iia5]
    # universe_id=2
    iia = openmc.Universe(name='zone_iia')
    iia.add_cells(_bound_zone_cells(elem_cells, level_bounds))
    return iia

def void_cell(elem_bound):
    elem_bound = elem_bound.clone()
    c1 = openmc.Cell(region=elem_bound, name='lattice_void')
    #universe_id=5
    v = openmc.Universe(name='lattice_void')
    v.add_cell(c1)
    return v

def graphite_triangles(elem_bound, moder, fuel):
    s1 = openmc.Plane(1.0, 1.0, 0.0, 0.0)
    s2 = openmc.Plane(-1.0, 1.0, 0.0, 0.0)
    s3 = openmc.Plane(1.0, -1.0, 0.0, 0.0)
    s4 = openmc.Plane(-1.0, -1.0, 0.0, 0.0)
    surfs = [(s4, 'bottom_left'),
             (s1, 'top_right'),
             (s2, 'top_left'),
             (s3, 'bottom_right')]
    univs = []
    for i, (s, name) in enumerate(surfs):
        elem_bound = elem_bound.clone()
        c1 = openmc.Cell(fill=moder, region=(-s & elem_bound))
        elem_bound = elem_bound.clone()
        c2 = openmc.Cell(fill=fuel, region=(+s & elem_bound))
        # universe_id = 6+i
        gr_tri = openmc.Universe(name=f'{name}_triangle')
        gr_tri.add_cells([c1, c2])
        univs.append(gr_tri)
    return univs
