import openmc
import numpy as np
import argparse

from openmc.deplete import CoupledOperator, PredictorIntegrator, CELIIntegrator

import core_elements as ce
import control_rods as cr
import root_geometry as rg

# Materials

fuel = openmc.Material(name='fuel')
fuel.set_density('g/cm3', density=3.3332642)
fuel.add_components({'Li': {'percent': 0.3585,
                            'enrichment': 95.995,
                            'enrichment_target': 'Li7',
                            'percent_type': 'ao'},
                     'F19': 0.5635666666666667,
                     'Be9': 0.05333333333333333,
                     'Th232': 0.024,
                     'U233': 0.0006},
                    percent_type='ao')
fuel.depletable = True
fuel.volume = 48710000.0

moder = openmc.Material(name='graphite')
moder.set_density('g/cm3', density=1.843)
moder.add_nuclide('C0', 1.000, percent_type='wo')
moder.add_s_alpha_beta('c_Graphite')

hast = openmc.Material(name='hastelloyN')
hast.set_density('g/cm3', density=8.671)
#hast.add_components({'Al27': 0.003,
#                     'Ni': 0.677,
#                     'W': 0.250,
#                     'Cr': 0.070},
#                    percent_type='wo')
hast.add_components({'Ni': 0.73709,
                     'Mo': 0.12,
                     'Cr': 0.07,
                     'Fe': 0.03,
                     'C': 0.0006,
                     'Mn': 0.0035,
                     'Si': 0.001,
                     'W': 0.001,
                     'Al': 0.001,
                     'Ti': 0.0125, #avg
                     'Cu': 0.001,
                     'Co': 0.002,
                     'P': 0.00015,
                     'S': 0.00015,
                     'B': 0.000010,
                     'Hf': 0.01,
                     'Nb': 0.01},
                    percent_type='wo')

mat = openmc.Materials(materials=[fuel, moder, hast])
mat.export_to_xml()

colormap = {moder: 'purple',
            hast: 'blue',
            fuel: 'yellow'}

def parse_arguments():
    """Parses arguments from command line.

    Returns
    -------
    deplete : bool
        Flag indicated whether or not to run a depletion simulation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--deplete',
                        type=bool,
                        default=False,
                        help='flag for running depletion')

    args = parser.parse_args()
    return bool(args.deplete)

def shared_elem_geometry(elem_type,
                         gr_sq_d,
                         gr_sq_r,
                         r_rib,
                         l1,
                         l2,
                         l3,
                         r_es,
                         es_name):
    """Creates surfaces and regions for lattice elements.

    Parameters
    ----------
    elem_type : 'core', 'cr'
        Indicates the type of element. 'core' inidcates for Zones IA and IIA.
        'cr' indicates control rod.
    gr_sq_d : float
        Half-width of graphite square element in cm.
    gr_sq_r : float
        Radius of graphite square rounded corners in cm.
    r_rib : float
        Radius of graphite element rib section.
    l1 : float
        Coordinate used to position graphite element ribs and rib tips.
    l2 : float
        Coordinate used to position graphite element ribs.
    l3 : float
        Coordinate used to position graphite element rib tips.
    r_es : float
        Radius of extra cylindrical surface used for element
    es_name : str
        Name of extra cylindrical surface.

    Returns
    -------
    gr_sq_neg : openmc.Intersection
        The region bounding the outer surface of the graphite
        element.
    gr_extra_regions : list of (openmc.Region, str)
        'Add-on' regions and their names for the graphite element.
        Includes ribs, rib tips, and gap-filling regions.
    inter_elem_channel : openmc.Region, list of (openmc.Region, str)
        Inter-element channel region(s)
    extra_surf : openmc.ZCylinder
        Extra cylindrical surface used in the element.
    """
    # Square graphite element
    gr_sq_neg = openmc.rectangular_prism(gr_sq_d*2,
                                         gr_sq_d*2,
                                         corner_radius=gr_sq_r)

    # Rib tip surfaces
    ul_t = openmc.ZCylinder(-l1, -l3, r_rib, name='rib_ul_tip')
    br_t = openmc.ZCylinder(l1, l3, r_rib, name='rib_br_tip')
    ru_t = openmc.ZCylinder(-l3, l1, r_rib, name='rib_ru_tip')
    lb_t = openmc.ZCylinder(l3, -l1, r_rib, name='rib_lb_tip')

    # Graphite element rib tip regions
    rib_ul_t = -ul_t
    rib_br_t = -br_t
    rib_ru_t = -ru_t
    rib_lb_t = -lb_t

    if elem_type == 'core':
        # Graphite element ribs for zones I-A and II-A
        ul = openmc.ZCylinder(-l1, l2, r_rib, name='rib_ul')
        br = openmc.ZCylinder(l1, -l2, r_rib, name='rib_br')
        lb = openmc.ZCylinder(-l2, -l1, r_rib, name='rib_lb')
        ru = openmc.ZCylinder(l2, l1, r_rib, name='rib_ru')

        # Graphite element rib regions.
        rib_ul = -ul
        rib_br = -br
        rib_lb = -lb
        rib_ru = -ru

        # inter-element fuel channel region
        inter_elem_channel = +ul & +br & +lb & +ru

    elif elem_type == 'cr':
        # Parameters for control rod element
        r_d = 1.16
        e_d = 2 * r_d / np.sqrt(3)
        r_c = 0.18

        # Base rib region
        ul = openmc.model.hexagonal_prism(origin=(-l1, l2), edge_length=e_d,
                                          orientation='x', corner_radius=r_c)
        br = openmc.model.hexagonal_prism(origin=(l1, -l2), edge_length=e_d,
                                          orientation='x',corner_radius=r_c)
        lb = openmc.model.hexagonal_prism(origin=(-l2, -l1), edge_length=e_d,
                                          orientation='y',corner_radius=r_c)
        ru = openmc.model.hexagonal_prism(origin=(l2, l1), edge_length=e_d,
                                          orientation='y',corner_radius=r_c)

        rib_ul = ul
        rib_lb = br
        rib_br = lb
        rib_ru = ru

        inter_elem_channel = ~ul & ~br & ~lb & ~ru

    ribs = [[rib_ul, 'rib_ul'],
            [rib_br, 'rib_br'],
            [rib_ru, 'rib_ru'],
            [rib_lb, 'rib_lb'],
            [rib_ul_t, 'rib_ul_t'],
            [rib_br_t, 'rib_br_t'],
            [rib_ru_t, 'rib_ru_t'],
            [rib_lb_t, 'rib_lb_t']]

    gr_extra_regions = ribs
    inter_elem_channel = inter_elem_channel & +ul_t & +br_t & +ru_t & +lb_t

    extra_surf = openmc.ZCylinder(r=r_es, name=es_name)

    return gr_sq_neg, gr_extra_regions, inter_elem_channel, extra_surf

def cr_lattice(cr_boundary, core_base, core_top):
    """Creates the control rod lattice.

    Parameters
    ----------
    cr_boundary : openmc.Intersection
        Outer bound of the lattice in the xy-plane.
    core_base : openmc.ZPlane
        Core bottom bounding surface.
    core_top : openmc.ZPlane
        Core top bounding surface.

    Returns
    -------
    c1 : openmc.Cell
        Cell containing the control rod lattice.

    """
    (gr_sq_neg,
     gr_extra_regions,
     inter_elem_channel,
     fuel_hole) = shared_elem_geometry('cr',
                                       7.23645,
                                       0.99,
                                       0.8,
                                       5.8801,
                                       6.505,
                                       8.03646,
                                       5.08,
                                       'cr_fuel_hole')

    f = cr.control_rod(gr_sq_neg,
                       gr_extra_regions,
                       inter_elem_channel,
                       fuel_hole,
                       fuel,
                       moder)
    e = cr.control_rod_channel(gr_sq_neg,
                               gr_extra_regions,
                               inter_elem_channel,
                               fuel_hole,
                               fuel,
                               moder)

    cl = openmc.RectLattice()
    cl.pitch = np.array([15.24, 15.24])
    N = 2 / 2
    cl.lower_left = -1 * cl.pitch * N
    cl.universes = [[f, e],
                    [e, f]]
    c1 = openmc.Cell(fill=cl, region=(+core_base & -core_top & cr_boundary),
                     name='cr_lattice')

    return c1

def main_lattice(zone_i_boundary, cr_boundary, core_base, core_top):
    """Creates the core lattice.

    Parameters
    ----------
    zone_i_boundary : 3-tuple of openmc.model.IsogonalOctagon
        Zone I bounding surfaces in the xy-plane
    cr_boundary : openmc.Intersection
        Outer bound of the lattice in the xy-plane.
    core_base : openmc.ZPlane
        Core bottom bounding surface.
    core_top : openmc.ZPlane
        Core top bounding surface.

    Returns
    -------
    main_cells : list of openmc.Cell
        Cells containing the main lattice.

    """
    (gr_sq_neg,
     gr_extra_regions,
     inter_elem_channel,
     gr_round_4) = shared_elem_geometry('core',
                                        4.953,
                                        0.46,
                                        0.66802,
                                        4.28498,
                                        4.53898,
                                        5.62102,
                                        2.2225,
                                        'gr_round_4')
    l = ce.zoneIA(gr_sq_neg,
                  gr_extra_regions,
                  inter_elem_channel,
                  gr_round_4,
                  moder,
                  fuel,
                  hast)
    (gr_sq_neg,
     gr_extra_regions,
     inter_elem_channel,
     gr_round_4) = shared_elem_geometry('core',
                                        4.953,
                                        0.46,
                                        0.66802,
                                        4.28498,
                                        4.53898,
                                        5.62102,
                                        2.2225,
                                        'gr_round_4')

    z = ce.zoneIIA(gr_sq_neg,
                   gr_extra_regions,
                   inter_elem_channel,
                   gr_round_4,
                   moder,
                   fuel)
    v = ce.void_cell()
    # tres, uno, dos, quatro
    t, u, d, q = ce.graphite_triangles(fuel, moder)

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

    c1 = openmc.Cell(fill=main, region=(+core_base &
                                        -core_top &
                                        +zone_i_boundary[2] &
                                        -zone_i_boundary[1] &
                                        ~cr_boundary), name='main_lattice_smaller_octader')
    c2 = openmc.Cell(fill=main, region=(+core_base &
                                        -core_top &
                                        -zone_i_boundary[2] &
                                        ~cr_boundary),
                     name='main_lattice_insite_smallest_octader')
    c3 = openmc.Cell(fill=main, region=(+core_base &
                                        -core_top &
                                        -zone_i_boundary[0] &
                                        +zone_i_boundary[1] &
                                        +zone_i_boundary[2] &
                                        ~cr_boundary),
                     name=('main_lattice_inside_base_octader'
                          '_deducted_smaller_smallest'))
    main_cells = [c1, c2, c3]
    return main_cells

def plot_geometry(name,
                  origin=(0.,0.,0.),
                  pixels=(10000,10000),
                  width=(686.816, 686.816),
                  color_by='material',
                  colormap=colormap,
                  basis='xy'):
    plot = openmc.Plot(name=name)
    plot.origin = origin
    plot.pixels = pixels
    plot.width = width
    plot.color_by = color_by
    plot.colors = colormap
    plot.basis = basis

    return plot


deplete = parse_arguments()

(zone_bounds,
 core_bounds,
 reflector_bounds,
 vessel_bounds) = rg.shared_root_geometry()

(cr_boundary,
 zone_i_boundary,
 zone_ii_boundary) = zone_bounds

(annulus_boundary,
 lower_plenum_boundary,
 core_base,
 core_top) = core_bounds

(radial_reflector_boundary,
 bottom_reflector_boundary,
 top_reflector_boundary) = reflector_bounds

(radial_vessel_boundary,
 bottom_vessel_boundary,
 top_vessel_boundary) = vessel_bounds

main = main_lattice(zone_i_boundary,
                    cr_boundary,
                    core_base,
                    core_top)

cr = cr_lattice(cr_boundary,
                core_base,
                core_top)

iib = rg.zoneIIB(zone_i_boundary,
                 zone_ii_boundary,
                 core_base,
                 core_top,
                 fuel,
                 moder)

a = rg.annulus(zone_ii_boundary,
               annulus_boundary,
               core_base,
               core_top,
               fuel)

lp = rg.lower_plenum(core_base,
                     lower_plenum_boundary,
                     annulus_boundary,
                     fuel)

rr, rb, rt = rg.reflectors(annulus_boundary,
                           radial_reflector_boundary,
                           lower_plenum_boundary,
                           bottom_reflector_boundary,
                           core_top,
                           top_reflector_boundary,
                           moder)

vr, vb, vt = rg.vessel(radial_reflector_boundary,
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
settings.temperature = {'default': 900,
                        'method': 'interpolation',
                        'range': (800, 1000)}
settings.export_to_xml()

## Slice plots

plots = openmc.Plots()

plots.append(plot_geometry('serpent-plot1',
                           origin=(0., 0., 150.5)))
plots.append(plot_geometry('serpent-plot2',
                           origin=(0., -77.5, 306.07),
                           pixels=(1550, 3400),
                           width=(155, 612.14),
                           basis='yz'))
plots.append(plot_geometry('serpent-plot3',
                           origin=(0., 0., 155.),
                           pixels=(1000, 1000),
                           width=(40, 40),
                           basis='yz'))
plots.append(plot_geometry('serpent-plot4',
                           origin=(16.5, 0., 306.07),
                           pixels=(2000, 2000),
                           width=(686.816, 612.14),
                           basis='yz'))
plots.append(plot_geometry('detail-zoneIA-IIA-lower1',
                           origin=(215, 0., 10.0),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIA-main',
                           origin=(215, 0., 23.0),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIA-upper1',
                           origin=(215, 0., 420),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIIA-upper',
                           origin=(215, 0., 435),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIIA-upper2',
                           origin=(215, 0., 437),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIA-upper2',
                           origin=(215, 0., 439),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIIA-upper3',
                           origin=(215, 0., 440),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIIA-upper4',
                           origin=(215, 0., 442),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('detail-zoneIA-upper3',
                           origin=(215, 0., 448),
                           pixels=(1000, 1000),
                           width=(40, 40)))
plots.append(plot_geometry('full-zoneIA-IIA-lower1',
                           origin=(0., 0., 10.0),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIA-main',
                           origin=(0., 0., 23.0),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIA-upper1',
                           origin=(0., 0., 420),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIIA-upper',
                           origin=(0., 0., 435),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIIA-upper2',
                           origin=(0., 0., 437),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIA-upper2',
                           origin=(0., 0., 439),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIIA-upper3',
                           origin=(0., 0., 440),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIIA-upper4',
                           origin=(0., 0., 442),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('full-zoneIA-upper3',
                           origin=(0., 0., 448),
                           width=(522.232, 522.232)))
plots.append(plot_geometry('detail-core-xz-upper',
                           origin=(215, 0., 440),
                           pixels=(1000, 1000),
                           width=(100, 100),
                           basis='xz'))
plots.append(plot_geometry('full-core-xz',
                           origin=(0., 0., 306.07),
                           pixels=(10000,10000),
                           width=(618.816, 612.14),
                           basis='xz'))
plots.export_to_xml()

if deplete:
    # Serpent fission q values
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
    op = CoupledOperator(model,
                         chain_file='chain_endfb71_pwr.xml',
                         fission_q=fiss_q)
    timesteps = [3] * 12
    integrator = PredictorIntegrator(op,
                                     timesteps,
                                     timestep_units='d',
                                     power=2.25e9)
    integrator.integrate()
