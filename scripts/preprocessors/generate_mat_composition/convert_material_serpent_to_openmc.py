import re
import sys

import openmc
from pathlib import Path
import neutronics_material_maker as nmm  # you'll need to install this manually

from saltproc.depcode import convert_nuclide_name_serpent_to_zam

WO_REGEX = "\\-[0-9]+\\."
COMP_REGEX = "\\-?[0-9]+\\.[0-9]+E?(\\+|\\-)?[0-9]{0,2}"
MATERIAL_REGEX = "^\\s*[^%]*\\s*mat\\s+[a-zA-Z0-9]+\\s+" + COMP_REGEX
NUCLIDE_REGEX_1 = "^\\s*[^%]*\\s*[0-9]{4,}\\.[0-9]{2}c\\s+" + COMP_REGEX
# decay only nuclides
NUCLIDE_REGEX_2 = "^\\s*[^%]*\\s*[0-9]{5,}\\s+" + COMP_REGEX
ELEMENT_REGEX = "^\\s*[^%]*\\s*[0-9]+0{3}\\.[0-9]{2}c\\s+" + COMP_REGEX
THERM_REGEX = "^\\s*[^%]*\\s*(therm|thermstoch)\\s+[a-z]+"

S_a_b_dict = {
    'be': ['c_Be'],
    'hw': ['c_D_in_D2O'],
    'gr': ['c_Graphite'],
    'lw': ['c_H_in_H2O'],
    'hzr': ['c_H_in_ZrH', 'c_Zr_in_ZrH'],
    'poly': ['c_H_in_CH2']
}

# read command line input
try:
    serpent_mat_path = str(sys.argv[1])
except IndexError:
    raise SyntaxError("No file specified")

fname = serpent_mat_path.split('/').pop(-1).split('.')[0]
path = Path(serpent_mat_path).parents[0]

mat_file = []
with open(serpent_mat_path, 'r') as file:
    mat_file = file.readlines()

openmc_materials = openmc.Materials([])
# read serpent materials
for line in mat_file:
    if re.search(MATERIAL_REGEX, line):
        # Check if we've hit a new material

        # get info about material
        openmc_material = openmc.Material()
        mat_data = line.split()
        mat_name = mat_data[1]
        mat_dens = mat_data[2]

        # set name and density
        openmc_material.name = str(mat_name)
        if re.search(WO_REGEX, mat_data[2]):
            density_unit = 'g/cm3'
        else:
            density_unit = 'atom/cm3'

        openmc_material.set_density(density_unit, abs(float(mat_dens)))


        mat_cards = ['vol', 'burn', 'tmp', 'tms']
        for card in mat_cards:
            card_data = []
            if card in mat_data:
                val = mat_data[mat_data.index(card) + 1]
                if card == 'vol':
                    openmc_material.volume = float(val)
                elif card == 'tmp' or card == 'tms':
                    openmc_material.temperature = float(val)
                elif card == 'burn':
                    openmc_material.depletable = bool(int(val))

        openmc_materials.append(openmc_material)

    elif re.search(ELEMENT_REGEX, line) or re.search(NUCLIDE_REGEX_1, line): # or re.search(NUCLIDE_REGEX_2, line):
        # get info about element
        component_info = line.split()
        component_code = component_info[0].split('.')[0]
        percent = component_info[1]

        # for decay only nuclides there's a zero
        # on the end of the nuclide code
        # indcated the ground state
        #if re.search(NUCLIDE_REGEX_2, line):
        #    component_code = component_code[:-1]

        # get info about nuclide
        # need to switch reading into OpenMC directly
        # to handle the case where nuclides in one
        # Material have a difference percent type
        if re.search(WO_REGEX, percent):
            percent_type = 'wo'
        else:
            percent_type = 'ao'

        metastable = False
        if component_code[-3] == '3':
            metastable = True
            component_code = str(convert_nuclide_name_serpent_to_zam(component_code))
            # remove the 0 at the end of the
            # nuclide code that our helper function
            # adds to it.
            component_code = component_code[:-1]
        if metastable:
            component_name += 'm'

        component_name = nmm.zaid_to_isotope(component_code)
        if re.search(ELEMENT_REGEX, line):
            component_name = component_name[:-1]
        elif metastable:
            component_name += 'm'
        else:
            pass
        openmc_materials[-1].add_components({component_name: abs(float(percent))}, percent_type)

    elif re.search(THERM_REGEX, line):
        data = line.split()[2:]
        for item in data:
            table_name = item.split('.')[0]
            table_name = table_name[:-2]
            if bool(S_a_b_dict.get(table_name)):
                for openmc_sab_name in S_a_b_dict[table_name]:
                    openmc_materials[-1].add_s_alpha_beta(openmc_sab_name)

openmc_materials.export_to_xml(path / f'{fname}.xml')
