import openmc
import numpy as np
from openmc.deplete import CoupledOperator, PredictorIntegrator, CELIIntegrator

from _core_elements_optimized import *
from _control_rods_optimized import *
from _root_geometry_optimized import *

# Materials

T = 900
fuel = openmc.Material(name='fuel', temperature=T)
fuel.set_density('g/cm3', density=3.35)
fuel.add_components({'Li7': 0.0787474673879085,
                     'Be9': 0.0225566879138321,
                     'F19': 0.454003012179284,
                     'Th232': 0.435579130482336,
                     'U233': 0.00911370203663893},
                    percent_type='wo')
fuel.depletable = True
fuel.volume = 48710000.0

moder = openmc.Material(name='graphite', temperature=T)
moder.set_density('g/cm3', density=1.84)
moder.add_nuclide('C0', 1.000, percent_type='wo')
moder.add_s_alpha_beta('c_Graphite')

hast = openmc.Material(name='hastelloyN', temperature=T)
hast.set_density('g/cm3', density=8.671)
hast.add_components({'Al27': 0.003,
                     'Ni': 0.677,
                     'W': 0.250,
                     'Cr': 0.070},
                    percent_type='wo')

mat = openmc.Materials(materials=[fuel, moder, hast])
mat.export_to_xml()

# Geometry
def cr_lattice(cr_boundary, core_base, core_top):
    fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel = shared_cr_geometry()
    f = control_rod(fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, fuel, moder)
    fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel = shared_cr_geometry()
    e = control_rod_channel(fuel_hole, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, fuel, moder)

    cr = openmc.RectLattice()
    cr.pitch = np.array([15.24, 15.24])
    N = 2 / 2
    cr.lower_left = -1 * cr.pitch * N
    cr.universes = [[e, f],
                    [f, e]]
    c1 = openmc.Cell(fill=cr, region=(+core_base & -core_top & cr_boundary), name='cr_lattice')

    return c1

def main_lattice(zone_i_boundary, cr_boundary, core_base, core_top):
    elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4 = shared_elem_geometry()
    l = zoneIA(elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4, moder, fuel, hast)
    elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4 = shared_elem_geometry()
    z = zoneIIA(elem_bound, gr_sq_neg, gr_corners, gr_t, inter_elem_channel, gr_round_4, moder, fuel)
    v = void_cell(elem_bound)
    # tres, uno, dos, quatro
    t, u, d, q = graphite_triangles(elem_bound, moder, fuel)

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
    c1 = openmc.Cell(fill=main, region=(+core_base & -core_top & zone_i_boundary & ~cr_boundary), name='main_lattice')
    return c1

zone_bounds, core_bounds, reflector_bounds, vessel_bounds = shared_root_geometry()

cr_boundary, zone_i_boundary, zone_ii_boundary = zone_bounds
annulus_boundary, lower_plenum_boundary, core_base, core_top = core_bounds
radial_reflector_boundary, bottom_reflector_boundary, top_reflector_boundary = reflector_bounds
radial_vessel_boundary, bottom_vessel_boundary, top_vessel_boundary= vessel_bounds

main = main_lattice(zone_i_boundary, cr_boundary, core_base, core_top)
cr = cr_lattice(cr_boundary, core_base, core_top)
iib = zoneIIB(zone_i_boundary, zone_ii_boundary, annulus_boundary, core_base, core_top, moder, fuel)
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
univ = openmc.Universe()
univ.add_cells([cr, main, iib, lp, a, rr, rb, rt, vr, vb, vt])

geo.root_universe = univ
geo.remove_redundant_surfaces()
geo.export_to_xml()

# Settings
settings = openmc.Settings()
settings.particles = 10000
settings.batches = 150
settings.inactive = 25
settings.generations_per_batch = 1
settings.temperature = {'default': 900, 'method': 'interpolation', 'range': (800, 1000)}
#settings.temperature = {'default': 600, 'method': 'nearest'}
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

plot = openmc.Plot(name='serpent-plot-1_full-zoneIA-main')
plot.origin=(0, 0, 150.5)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='serpent-plot-2')
plot.origin=(0, -77.5, 200)
plot.width=(155, 700)
plot.pixels=(1550, 3400)
plot.color_by='material'
plot.colors=colormap
plot.basis='yz'
plots.append(plot)

plot = openmc.Plot(name='serpent-plot-3')
plot.origin=(0, 0, 155)
plot.width=(40, 40)
plot.pixels=detail_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='yz'
plots.append(plot)

plot = openmc.Plot(name='serpent-plot-4')
plot.origin=(16.5, 0, 200)
plot.width=(700, 700)
plot.pixels=(2000, 2000)
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
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper1')
plot.origin=(0, 0, 435)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-upper1')
plot.origin=(0, 0, 420)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper2')
plot.origin=(0, 0, 437)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-upper2')
plot.origin=(0, 0, 439)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper3')
plot.origin=(0, 0, 440)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIA-upper3')
plot.origin=(0, 0, 448)
plot.width=(600, 600)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xy'
plots.append(plot)

plot = openmc.Plot(name='full-zoneIIA-upper4')
plot.origin=(0, 0, 442)
plot.width=(600, 600)
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
plot.origin=(0, 0, 200)
plot.width=(700, 700)
plot.pixels=full_pixels
plot.color_by='material'
plot.colors=colormap
plot.basis='xz'
plots.append(plot)

plots.export_to_xml()

DEPLETE = False
if DEPLETE:
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

