import openmc
import numpy as np

def control_rod(gr_sq_neg, gr_corners, inter_elem_channel, fuel_hole, fuel, moder, optimized):
    s1 = openmc.ZCylinder(r=4.7625, name='control_rod')

    c1 = openmc.Cell(fill=moder, region=-s1, name='control_rod')
    c2 = openmc.Cell(fill=fuel, region=(+s1 & -fuel_hole), name='cr_fuel_inner')
    if optimized:
        c3 = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg), name='cr_moderator_core')

        #universe_id=3
        cr = openmc.Universe(name='control_rod', cells=[c1, c2, c3])

        for (reg, name) in inter_elem_channel:
            cr.add_cell(openmc.Cell(fill=fuel, region=reg, name=f'cr_fuel_outer_{name}'))
    else:
        c3 = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg & inter_elem_channel),
                         name='cr_moderator')
        c4 = openmc.Cell(fill=fuel, region= (~gr_sq_neg & inter_elem_channel),
                         name='cr_fuel_outer')
        #universe_id=3
        cr = openmc.Universe(name='control_rod', cells=[c1, c2, c3, c4])

    for (reg, name) in gr_corners:
            cr.add_cell(openmc.Cell(fill=moder, region=reg, name=f'cr_moderator_{name}'))

    return cr

def control_rod_channel(gr_sq_neg, gr_corners, inter_elem_channel, fuel_hole, fuel, moder, optimized):
    c1 = openmc.Cell(fill=fuel, region=(-fuel_hole), name='crc_fuel_inner')

    if optimized:
        c2 = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg), name='crc_moderator_core')

        # universe_id=4
        crc = openmc.Universe(name='control_rod_channel', cells=[c1, c2])

        for (reg, name) in inter_elem_channel:
            crc.add_cell(openmc.Cell(fill=fuel, region=reg, name=f'crc_fuel_outer_{name}'))
    else:
        c2 = openmc.Cell(fill=moder, region=(+fuel_hole & gr_sq_neg & inter_elem_channel), name='crc_moderator')
        c3 = openmc.Cell(fill=fuel, region=(~gr_sq_neg & inter_elem_channel), name='crc_fuel_outer')

        # universe_id=4
        crc = openmc.Universe(name='control_rod_channel', cells=[c1, c2, c3])

    for (reg, name) in gr_corners:
        crc.add_cell(openmc.Cell(fill=moder, region=reg, name=f'crc_moderator_{name}'))


    return crc
