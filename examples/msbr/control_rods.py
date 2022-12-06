import openmc
import numpy as np

def control_rod(gr_sq_neg,
                gr_extra_regions,
                inter_elem_channel,
                fuel_hole,
                fuel,
                moder):
    """Create universe for control rod element with control rod fully inserted.
    Based on specification in Roberton, 1971.

    Parameters
    ----------
    gr_sq_neg : openmc.Intersection
        The region bounding the outer surface of the 6 in. x 6 in. graphite
        element.
    gr_extra_regions : list of (openmc.Region, str)
        'Add-on' regions and their names for the graphite element.
        Includes ribs, rib tips, and gap-filling regions.
    inter_elem_channel : openmc.Region, list of (openmc.Region, str)
        Inter-element channel region(s).
    fuel_hole : openmc.ZCylinder
        Central fuel hole in graphite element.
    fuel : openmc.Material
        Fuel salt material
    moder : openmc.Material
        Graphite material

    Returns
    -------
    cr : openmc.Universe
        Univerese for control rod element with control rod fully insterted.
    """

    s1 = openmc.ZCylinder(r=4.7625, name='control_rod')

    c1 = openmc.Cell(fill=moder, region=-s1, name='control_rod')
    c2 = openmc.Cell(fill=fuel, region=(+s1 & -fuel_hole), name='cr_fuel_inner')
    c3 = openmc.Cell(fill=moder, region=(+fuel_hole &
                                         gr_sq_neg &
                                         inter_elem_channel),
                     name='cr_moderator')
    c4 = openmc.Cell(fill=fuel, region= (~gr_sq_neg & inter_elem_channel),
                     name='cr_fuel_outer')
    #universe_id=3
    cr = openmc.Universe(name='control_rod', cells=[c1, c2, c3, c4])

    for (reg, name) in gr_extra_regions:
            cr.add_cell(openmc.Cell(fill=moder, region=reg,
                                    name=f'cr_moderator_{name}'))

    return cr

def control_rod_channel(gr_sq_neg,
                        gr_extra_regions,
                        inter_elem_channel,
                        fuel_hole,
                        fuel,
                        moder):
    """Create universe for control rod element with control rod fully withdrawn.
    Based on specification in Roberton, 1971.

    Parameters
    ----------
    gr_sq_neg : openmc.Intersection
        The region bounding the outer surface of the 6 in. x 6 in. graphite
        element.
    gr_extra_regions : list of (openmc.Region, str)
        'Add-on' regions and their names for the graphite element.
        Includes ribs, rib tips, and gap-filling regions.
    inter_elem_channel : openmc.Region, list of (openmc.Region, str)
        Inter-element channel region(s).
    fuel_hole : openmc.ZCylinder
        Central fuel hole in graphite element.
    fuel : openmc.Material
        Fuel salt material
    moder : openmc.Material
        Graphite material

    Returns
    -------
    crc : openmc.Universe
        Universe for control rod element with control rod fully withdrawn.
    """

    c1 = openmc.Cell(fill=fuel, region=(-fuel_hole), name='crc_fuel_inner')

    c2 = openmc.Cell(fill=moder, region=(+fuel_hole &
                                         gr_sq_neg &
                                         inter_elem_channel),
                     name='crc_moderator')
    c3 = openmc.Cell(fill=fuel, region=(~gr_sq_neg & inter_elem_channel),
                     name='crc_fuel_outer')

    # universe_id=4
    crc = openmc.Universe(name='control_rod_channel', cells=[c1, c2, c3])

    for (reg, name) in gr_extra_regions:
        crc.add_cell(openmc.Cell(fill=moder, region=reg,
                                 name=f'crc_moderator_{name}'))

    return crc
