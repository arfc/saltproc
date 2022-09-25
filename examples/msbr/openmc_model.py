import openmc
import numpy as np

from _core_elements import *
from _control_rods import *
from _root_geometry import *

# Materials

fuel = openmc.Material(name='fuel', temperature=900.0)
fuel.set_density('g/cm3', density=3.35)
fuel.add_components({'Li7': 0.0787474673879085,
                     'Be9': 0.0225566879138321,
                     'F19': 0.454003012179284,
                     'Th232': 0.435579130482336,
                     'U233': 0.00911370203663893},
                    percent_type='wo')
fuel.depletable = True
fuel.volume = 48710000.0

moder = openmc.Material(name='graphite', temperature=900.0)
moder.set_density('g/cm3', density=1.84)
moder.add_nuclide('C0', 1.000, percent_type='wo')
moder.add_s_alpha_beta('c_Graphite')

hast = openmc.Material(name='hastelloyN', temperature=900.0)
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
    fuel_hole, gr_sq_neg, gr_corners, inter_elem_channel = shared_cr_geometry()
    elem_bound = openmc.rectangular_prism(7.62*2, 7.62*2) # Pin outer boundary

    f = control_rod(fuel_hole, gr_sq_neg, gr_corners, inter_elem_channel, moder, fuel)
    e = control_rod_channel(fuel_hole, gr_sq_neg, gr_corners, inter_elem_channel, moder, fuel)

    cr = openmc.RectLattice()
    cr.pitch = np.array([15.24, 15.24])
    N = 2 / 2
    cr.lower_left = -1 * cr.pitch * N
    cr.universes = [[f, e],
                    [e, f]]
    c1 = openmc.Cell(fill=cr, region=(+core_base & -core_top & cr_boundary), name='cr_lattice')

    return c1

def main_lattice(zone_i_boundary, cr_boundary, core_base, core_top):
    elem_bound, gr_corners, gr_sq_neg, inter_elem_channel, gr_round_4 = shared_elem_geometry()
    l = zoneIA(elem_bound, gr_corners, gr_sq_neg, inter_elem_channel, gr_round_4, moder, fuel, hast)
    z = zoneIIA(elem_bound, gr_corners, gr_sq_neg, inter_elem_channel, gr_round_4, moder, fuel)
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
iib_m, iib_f = zoneIIB(zone_i_boundary, zone_ii_boundary, annulus_boundary, core_base, core_top, moder, fuel)
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
univ.add_cells([cr, main, iib_m, iib_f, lp, a, rr, rb, rt, vr, vb, vt])

geo.root_universe = univ
geo.export_to_xml()

# Settings
settings = openmc.Settings()
settings.particles = 300
settings.batches = 400
settings.inative = 5
settings.temperature = {'default': 900, 'method': 'interpolation'}

# Plots
plots_3d = False
detail_pixels = (1000, 1000)
full_pixels = (10000, 10000)

colormap = {moder: 'purple',
            hast: 'blue',
            fuel: 'yellow'}
## Slice plots
plots = openmc.Plots()

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

plot = openmc.Plot(name='full-zoneIA-main')
plot.origin=(0, 0, 23.0)
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

if plots_3d:
    plot = openmc.Plot(name='full-core-3d')
    plot.origin=(0,0,220)
    plot.type = 'voxel'
    plot.color_by='materials'
    plot.colors=colormap
    plot.width = (700., 700., 650.)
    plot.pixels = (10000, 10000, 10000)

plots = openmc.Plots()
plots.append(plot)
plots.export_to_xml()

plots.export_to_xml()
