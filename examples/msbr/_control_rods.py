import openmc
import numpy as np

def shared_cr_geometry():
    fuel_hole = openmc.ZCylinder(r=5.08, name='cr_fuel_hole')
    elem_bound = openmc.rectangular_prism(7.62*2, 7.62*2) # Pin outer boundary

    gr_sq_neg = openmc.rectangular_prism(7.23646*2, 7.23646*2, corner_radius=0.99) # Graphite square
    # params for
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

    gr_corners = elem_bound & (ul | br | lb | ru |
                               -ul_t | -br_t | -ru_t | -lb_t)

    inter_elem_channel = (~gr_sq_neg & elem_bound &
                         ~ul & ~br & ~lb & ~ru &
                         +ul_t & +ru_t & +ru_t & +lb_t)


    return fuel_hole, gr_sq_neg, gr_corners, inter_elem_channel

def control_rod(fuel_hole, gr_sq_neg, gr_corners, inter_elem_channel, fuel, moder):
    s1 = openmc.ZCylinder(r=4.7625, name='control_rod')

    c1 = openmc.Cell(fill=moder, region=-s1, name='control_rod')
    c2 = openmc.Cell(fill=fuel, region=(+s1 & -fuel_hole), name='cr_fuel_inner')
    moderator_block = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg | gr_corners), name='cr_moderator')
    fuel_outer = openmc.Cell(fill=fuel, region=inter_elem_channel, name='cr_fuel_outer')
    #universe_id=3
    cr = openmc.Universe(name='control_rod')
    cr.add_cells([c1, c2, moderator_block, fuel_outer])
    return cr

def control_rod_channel(fuel_hole, gr_sq_neg, gr_corners, inter_elem_channel, fuel, moder):
    c1 = openmc.Cell(fill=fuel, region=(-fuel_hole), name='crc_fuel_inner')
    moderator_block = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg | gr_corners), name='crc_moderator')
    fuel_outer = openmc.Cell(fill=fuel, region=inter_elem_channel, name='crc_fuel_outer')
    # universe_id=4
    crc = openmc.Universe(name='control_rod_channel')
    crc.add_cells([c1, moderator_block, fuel_outer])
    return crc
