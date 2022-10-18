import openmc
import numpy as np

def shared_cr_geometry():
    fuel_hole = openmc.ZCylinder(r=5.08, name='cr_fuel_hole')
    elem_bound = openmc.rectangular_prism(7.62*2, 7.62*2) # Pin outer boundary
    eb_minx, eb_maxx, eb_miny, eb_maxy = list(elem_bound.get_surfaces().values())

    gr_sq_neg = openmc.rectangular_prism(7.23646*2, 7.23646*2, corner_radius=0.99) # Graphite square
    # params for
    (gr_minx, gr_maxx, gr_miny, gr_maxy,
    gr_cyl_lb, gr_cyl_minx, gr_cyl_miny,
    gr_cyl_ul, gr_cyl_maxy, gr_cyl_br,
    gr_cyl_maxx, gr_cyl_ru) = list(gr_sq_neg.get_surfaces().values())

    r_d = 1.16
    e_d = 2 * r_d / np.sqrt(3)
    r_dt = 0.8
    r_c = 0.18
    l1 = 5.8801
    l2 = 6.505
    l3 = 8.03646
    ul = openmc.model.hexagonal_prism(origin=(-l1, l2), edge_length=e_d, orientation='x', corner_radius=r_c)
    br = openmc.model.hexagonal_prism(origin=(l1, -l2), edge_length=e_d, orientation='x',corner_radius=r_c)
    lb = openmc.model.hexagonal_prism(origin=(-l2, -l1), edge_length=e_d, orientation='y',corner_radius=r_c)
    ru = openmc.model.hexagonal_prism(origin=(l2, l1), edge_length=e_d, orientation='y',corner_radius=r_c)
    ul_t = openmc.ZCylinder(-l1, -l3, r_dt, name='corner_ul_tip')
    br_t = openmc.ZCylinder(l1, l3, r_dt, name='corner_br_tip')
    ru_t = openmc.ZCylinder(-l3, l1, r_dt, name='corner_ru_tip')
    lb_t = openmc.ZCylinder(l3, -l1, r_dt, name='corner_lb_tip')

    gr_ul = ul & -eb_maxy & +gr_maxy
    gr_ul_fill = ul & +gr_cyl_ul & -gr_maxy & -gr_cyl_minx & +gr_cyl_maxy
    gr_br = br & +eb_miny & -gr_miny
    gr_br_fill = br & +gr_cyl_br & +gr_miny & +gr_cyl_maxx & -gr_cyl_miny
    gr_lb = lb & +eb_minx & -gr_minx
    gr_lb_fill = lb & +gr_cyl_lb & +gr_minx & -gr_cyl_minx & -gr_cyl_miny
    gr_ru = ru & -eb_maxx & +gr_maxx
    gr_ru_fill = ru & +gr_cyl_ru & -gr_maxx & +gr_cyl_maxx & +gr_cyl_maxy

    gr_ul_t = -ul_t & +eb_miny & -gr_miny
    gr_br_t = -br_t & -eb_maxy & +gr_maxy
    gr_ru_t = -ru_t & +eb_minx & -gr_minx
    gr_lb_t = -lb_t & -eb_maxx & +gr_maxx

    gr_corners = (gr_ul, gr_br, gr_lb, gr_ru, gr_ul_fill, gr_br_fill, gr_lb_fill, gr_ru_fill)
    gr_t = (gr_ul_t, gr_br_t, gr_ru_t, gr_lb_t)

    inter_elem_channel = (~gr_sq_neg & elem_bound &
                         ~ul & ~br & ~lb & ~ru &
                         +ul_t & +br_t & +ru_t & +lb_t)


    return fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel

def control_rod(fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, fuel, moder):
    s1 = openmc.ZCylinder(r=4.7625, name='control_rod')

    c1 = openmc.Cell(fill=moder, region=-s1, name='control_rod')
    c2 = openmc.Cell(fill=fuel, region=(+s1 & -fuel_hole), name='cr_fuel_inner')
    c3 = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg), name='cr_moderator')
    c4 = openmc.Cell(fill=fuel, region=inter_elem_channel, name='cr_fuel_outer')

    c3_ul = openmc.Cell(fill=moder, region=gr_corners[0], name='cr_moderator_ul')
    c3_br = openmc.Cell(fill=moder, region=gr_corners[1], name='cr_moderator_br')
    c3_ru = openmc.Cell(fill=moder, region=gr_corners[2], name='cr_moderator_ru')
    c3_lb = openmc.Cell(fill=moder, region=gr_corners[3], name='cr_moderator_lb')
    c3_ulf = openmc.Cell(fill=moder, region=gr_corners[4], name='cr_moderator_ul_fill')
    c3_brf = openmc.Cell(fill=moder, region=gr_corners[5], name='cr_moderator_br_fill')
    c3_ruf = openmc.Cell(fill=moder, region=gr_corners[6], name='cr_moderator_ru_fill')
    c3_lbf = openmc.Cell(fill=moder, region=gr_corners[7], name='cr_moderator_lb_fill')
    c3_ul_t = openmc.Cell(fill=moder, region=gr_t[0], name='cr_moderator_ul_t')
    c3_br_t = openmc.Cell(fill=moder, region=gr_t[1], name='cr_moderator_br_t')
    c3_ru_t = openmc.Cell(fill=moder, region=gr_t[2], name='cr_moderator_ru_t')
    c3_lb_t = openmc.Cell(fill=moder, region=gr_t[3], name='cr_moderator_lb_t')


    #universe_id=3
    cr = openmc.Universe(name='control_rod')
    cr.add_cells([c1, c2, c3, c4, c3_ul, c3_br, c3_ru, c3_lb, c3_ulf, c3_brf, c3_ruf, c3_lbf, c3_ul_t, c3_br_t, c3_ru_t, c3_lb_t])

    return cr

def control_rod_channel(fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, fuel, moder):
    c1 = openmc.Cell(fill=fuel, region=(-fuel_hole), name='crc_fuel_inner')
    c2 = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg), name='crc_moderator')
    c3 = openmc.Cell(fill=fuel, region=inter_elem_channel, name='crc_fuel_outer')

    c2_ul = openmc.Cell(fill=moder, region=gr_corners[0], name='crc_moderator_ul')
    c2_br = openmc.Cell(fill=moder, region=gr_corners[1], name='crc_moderator_br')
    c2_ru = openmc.Cell(fill=moder, region=gr_corners[2], name='crc_moderator_ru')
    c2_lb = openmc.Cell(fill=moder, region=gr_corners[3], name='crc_moderator_lb')
    c2_ulf = openmc.Cell(fill=moder, region=gr_corners[4], name='crc_moderator_ul_fill')
    c2_brf = openmc.Cell(fill=moder, region=gr_corners[5], name='crc_moderator_br_fill')
    c2_ruf = openmc.Cell(fill=moder, region=gr_corners[6], name='crc_moderator_ru_fill')
    c2_lbf = openmc.Cell(fill=moder, region=gr_corners[7], name='crc_moderator_lb_fill')
    c2_ul_t = openmc.Cell(fill=moder, region=gr_t[0], name='crc_moderator_ul_t')
    c2_br_t = openmc.Cell(fill=moder, region=gr_t[1], name='crc_moderator_br_t')
    c2_ru_t = openmc.Cell(fill=moder, region=gr_t[2], name='crc_moderator_ru_t')
    c2_lb_t = openmc.Cell(fill=moder, region=gr_t[3], name='crc_moderator_lb_t')

    # universe_id=4
    crc = openmc.Universe(name='control_rod_channel')
    crc.add_cells([c1, c2, c3, c2_ul, c2_br, c2_ru, c2_lb, c2_ulf, c2_brf, c2_ruf, c2_lbf, c2_ul_t, c2_br_t, c2_ru_t, c2_lb_t])

    return crc
