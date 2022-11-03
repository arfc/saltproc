import openmc
import numpy as np

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


