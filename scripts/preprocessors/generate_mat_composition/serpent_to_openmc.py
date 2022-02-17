import re
from pyne import serpent
import openmc
import nmm #you'll need to install this manually

# read command line input
serpent_mat_path = ...
fname = ...
mat_data = []
with open(serpent_mat_path, 'r') as file:
    mat_data = file.readlines()

# read serpent materials
MATERIAL_REGEX = ...
NUCLIDE_REGEX = ...
ELEMENT_REGEX = ...

my_mat = nmm.Material()
my_mat.isotopes={}
my_mat.elements={}

new_material=True
openmc_mats = openmc.Materials([])
# initalize openmc materials
for line in mat_data:
    if re.match(MATERIAL_REGEX, line):
        if current_material
            current_material = False
        else:
            current_material = True
            if my_mat.isotopes is empty:
                #remove isotopes
            if my_mat.elements is empty:
                #remove elements

            openmc_mats.append(my_mat)

        my_mat = nmm.Material()
        my_mat.isotopes={}
        my_mat.elements={}

        #get info about material
        ...

        name=
        volume=
        temperature=
        density_unity=
        percent_type=

        my_mat.name = name
        my_mat.density = density
        my_mat.density_unit = unit
        my_mat.percent_type = percent_type

    elif re.match(NUCLIDE_REGEX,line):
        #get info about nuclide
        nuc_code=
        comp=
        unit=

        nuc_name = ... #use openmc or nmm libraries to convert code toanme

        my_mat.isotopes[nuc_name] = comp

    elif re.match(ELEMENT_REGEX,line):
        # get info about element
        el_code=
        comp=
        unit=
        el_name = ...

        my_mat.elements[el_name] = comp
