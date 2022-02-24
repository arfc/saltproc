import re
import os
import sys
from pyne import nucname as pyname
import openmc
import neutronics_material_maker as nmm #you'll need to install this manually
from neutronics_material_maker import zaid_to_isotope

WO_REGEX = "\-[0-9]+\."
COMP_REGEX = "\-?[0-9]+\.[0-9]+E?(\+|\-)?[0-9]{0,2}"
MATERIAL_REGEX = "^\s*[^%]*\s*mat\s+[a-zA-Z0-9]+\s+" + COMP_REGEX
NUCLIDE_REGEX_1 = "^\s*[^%]*\s*[0-9]{4,}\.[0-9]{2}c\s+" + COMP_REGEX
NUCLIDE_REGEX_2 = "^\s*[^%]*\s*[0-9]{5,}\s+" + COMP_REGEX # decay only nuclides
ELEMENT_REGEX = "^\s*[^%]*\s*[0-9]+0{3}\.[0-9]{2}c\s+" + COMP_REGEX
THERM_REGEX = "^\s*[^%]*\s*(therm|thermstoch)\s+[a-z]+"

S_a_b_dict = {
    'be': ['c_Be'],
    'hw': ['c_D_in_D2O'],
    'gr': ['c_Graphite'],
    'lw': ['c_H_in_H2O'],
    'hzr': ['c_H_in_ZrH', 'c_Zr_in_ZrH'],
    'poly': ['c_H_in_CH2']
}

def convert_nuclide_name_serpent_to_zam(nuc_code):
        """Checks Serpent2-specific meta stable-flag for zzaaam. For instance,
        47310 instead of 471101 for `Ag-110m1`. Metastable isotopes represented
        with `aaa` started with ``3``.

        Parameters
        ----------
        nuc_code : str
            Name of nuclide in Serpent2 form. For instance, `47310`.

        Returns
        -------
        nuc_zzaam : int
            Name of nuclide in `zzaaam` form (`471101`).

        """
        zz = pyname.znum(nuc_code)
        aa = pyname.anum(nuc_code)
        if aa > 300:
            if zz > 76:
                aa_new = aa - 100
            else:
                aa_new = aa - 200
            zzaaam = str(zz) + str(aa_new) + '1'
        else:
            zzaaam = nuc_code
        return int(zzaaam)

# read command line input
try:
    serpent_mat_path = str(sys.argv[1])
except IndexError:
    raise SyntaxError("No file specified")

fname = serpent_mat_path.split('/').pop(-1).split('.')[0]
path = os.path.dirname(serpent_mat_path)

mat_data = []
with open(serpent_mat_path, 'r') as file:
    mat_data = file.readlines()

first_material=True
openmc_mats = openmc.Materials([])
# read serpent materials
for line in mat_data:
    if re.search(MATERIAL_REGEX, line):
        # Check if we've hit a new material
        if first_material:
            first_material = False
        else:
            if not bool(my_mat['isotopes']):
                my_mat.pop('isotopes')
            if not bool(my_mat['elements']):
                my_mat.pop('elements')

            S_a_b = my_mat.pop('S_a_b')
            S_a_b_tables = False
            if bool(S_a_b):
                S_a_b_tables = True

            depletable = my_mat.pop('depletable')
            my_mat = nmm.Material(**my_mat)
            openmc_mats.append(my_mat.openmc_material)
            openmc_mats[-1].depletable = depletable
            if bool(my_mat.volume_in_cm3):
                openmc_mats[-1].volume = my_mat.volume_in_cm3
            if S_a_b_tables:
                for t in S_a_b:
                    openmc_mats[-1].add_s_alpha_beta(t)

        my_mat = {}
        my_mat['isotopes']={}
        my_mat['elements']={}
        my_mat['S_a_b'] = []

        #get info about material
        my_mat_data = line.split()
        my_mat_map = {}
        mat_cards = ['vol','burn','tmp','tms']
        for card in mat_cards:
            data = []
            if card in my_mat_data:
                i = my_mat_data.index(card)
                if card in ['vol', 'tmp', 'tms']:
                    data = float(my_mat_data[i+1])
                if card in ['burn']:
                    data = int(my_mat_data[i+1])
                my_mat_map[card] = data
        my_mat['name'] = str(my_mat_data[1])
        my_mat['density'] = abs(float(my_mat_data[2]))

        ## Doesn't support sum option
        if re.search(WO_REGEX, my_mat_data[2]):
            density_unit='g/cm3'
        else:
            density_unit='atom/cm3'

        my_mat['density_unit'] = density_unit

        # set optional cards
        my_mat['depletable'] = False
        for card in my_mat_map:
            if card == 'vol':
                my_mat['volume_in_cm3'] = my_mat_map[card]
            if card == 'tms' or card == 'tmp':
                my_mat['temperature'] = my_mat_map[card]
                my_mat['temperature_to_neutronics_code'] = True
            if card == 'burn':
                if my_mat_map[card] == 1:
                    my_mat['depletable'] = True
    elif re.search(ELEMENT_REGEX,line):
        # get info about element
        elem_info = line.split()
        elem_code = elem_info[0].split('.')[0]
        comp = elem_info[1]

        #get info about nuclide
        # need to switch reading into OpenMC directly
        # to handle the case where nuclides in one
        # Material have a difference percent type
        if re.search(WO_REGEX, comp):
            percent_type='wo'
        else:
            percent_type='ao'

        elem_name = nmm.zaid_to_isotope(elem_code)
        elem_name = elem_name[:-1]
        my_mat['elements'][elem_name] = abs(float(comp))
        my_mat['percent_type'] = percent_type


    elif (re.search(NUCLIDE_REGEX_1, line) or
          re.search(NUCLIDE_REGEX_2, line)):
        nuclide_info = line.split()
        nuc_code = nuclide_info[0].split('.')[0]
        # for decay only nuclides there's a zero
        # on the end of the nuclide code
        # indcated the ground state
        if re.search(NUCLIDE_REGEX_2, line):
            nuc_code = nuc_code[:-1]
        metastable = False
        if nuc_code[-3] == '3':
            metastable = True
            nuc_code = str(convert_nuclide_name_serpent_to_zam(nuc_code))
            # remove the 0 at the end of the
            # nuclide code that our helper function
            # adds to it.
            nuc_code = nuc_code[:-1]
        comp = nuclide_info[1]
        #get info about nuclide
        if re.search(WO_REGEX, comp):
            percent_type='wo'
        else:
            percent_type='ao'

        nuc_name = nmm.zaid_to_isotope(nuc_code) #use openmc or nmm libraries to convert code toanme
        if metastable:
            nuc_name += 'm'

        my_mat['isotopes'][nuc_name] = abs(float(comp))
        my_mat['percent_type'] = percent_type

    elif re.search(THERM_REGEX,line):
        data = line.split()[2:]
        for item in data:
            table_name = item.split('.')[0]
            table_name = table_name[:-2]
            if bool(S_a_b_dict.get(table_name)):
                if S_a_b_dict[table_name][0] not in my_mat['S_a_b']:
                    my_mat['S_a_b'] += S_a_b_dict[table_name]

openmc_mats.export_to_xml(os.path.join(path, fname+'.xml'))
