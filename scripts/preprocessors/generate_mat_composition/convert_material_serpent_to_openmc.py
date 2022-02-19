import re
import os
import sys
from pyne import serpent
import openmc
import neutronics_material_maker as nmm #you'll need to install this manually
from nmm import zaid_to_isotope

# read command line input

try:
    serpent_mat_path = sys.argv[1]
except IndexError:
    raise SyntaxError("No file specified")

fname = serpent_mat_path.split('/').pop(-1)
fname = fname.split('.')[0]
path = ''
for p in serpent_mat_path:
    path = os.path.join(path, p)

mat_data = []
with open(serpent_mat_path, 'r') as file:
    mat_data = file.readlines()

# read serpent materials
WO_REGEX = "\-[0-9]+\."
MATERIAL_REGEX = "mat [a-zA-Z]+ [0-9]+\.*[0-9]*" # need to add machinery for more cards
COMP_REGEX = "\-*[0-9]+\.[0-9]+E\+*\-*[0-9]{2}"
NUCLIDE_REGEX1 = "[0-9]{4,}\.[0-9]{2}c\s+" + COMP_REGEX
NUCLIDE_REGEX2 = "[0-9]{5,}\s+" + COMP_REGEX
ELEMENT_REGEX = "[0-9]+0{3}\.[0-9]{2}c\s+" + COMP_REGEX


new_material=True
openmc_mats = openmc.Materials([])

for line in mat_data:
    if re.match(MATERIAL_REGEX, line):
        # Check if we've hit a new material
        if current_material
            current_material = False
        else:
            current_material = True
            if my_mat['isotopes'] is empty:
                my_mat.pop('isotopes')
            if my_mat['elements'] is empty:
                my_mat.pop('elements')

            my_mat = nmm.Material(my_mat)
            openmc_mats.append(my_mat.openmc_material)

        my_mat = {}
        my_mat['isotopes']={}
        my_mat['elements']={}

        #get info about material
        my_mat_data = line.split()
        my_mat_map = {}
        mat_cards = ['vol'] # add support for more cards later
        for item in mat_cards:
            if item in my_mat_data:
                i = my_mat_data.index(item)
                my_mat_map[item] = my_mat_data[i+1]

        my_mat['name'] = my_mat_data[1]
        my_mat['density'] = abs(float(my_mat_data[2]))
        ## Doesn't support sum option
        if re.search(WO_REGEX, my_mat_data[2]):
            density_unit='g/cm3'
        else:
            density_unit='atom/cm3'

        my_mat['density_unit'] = density_unit

    elif (re.match(NUCLIDE_REGEX_1, line) or
          re.match(NUCLIDE_REGEX_2, line)):
        nuc_code, comp = line.split()
        #get info about nuclide
        if re.search(WO_REGEX, comp):
            percent_type='wo'
        else:
            percent_type='ao'

        nuc_name = nmm.zaid_to_isotope(nuc_code) #use openmc or nmm libraries to convert code toanme

        my_mat['isotopes'][nuc_name] = abs(float(comp))
        my_mat['percent_type'] = percent_type

    elif re.match(ELEMENT_REGEX,line):
        # get info about element
        elem_code,comp = line.split()

        elem_name = nmm.zaid_to_isotope(elem_code)
        my_mat['elements'][elem_name] = abs(float(comp))


openmc_mats.to_xml(os.path.join(path, fname+'.xml'))
