import re
import os
import sys
from scipy.spatial.transform import Rotation as sprot
import openmc
import _script_helpers as schp
# Read command line input

try:
    serpent_geo_path = str(sys.argv[1])
except IndexError:
    raise SyntaxError("No geo file specified")

try:
    openmc_mat_path = str(sys.argv[2])
except IndexError:
    raise SyntaxError("No material file specified")

schp.surf_dict = {}
schp.cell_dict = {}
schp.mat_dict = {}
schp.universe_dict = {}
schp.universe_to_cell_names_dict = {}
schp.geo_data = []

# get filenames
fname = serpent_geo_path.split('/').pop(-1).split('.')[0]
path = os.path.dirname(serpent_geo_path)
openmc_mats = openmc.Materials.from_xml(openmc_mat_path)
# global mat_dict = {}
for mat in openmc_mats:
    schp.mat_dict[mat.name] = mat
# add void material
schp.mat_dict['void'] = None

with open(serpent_geo_path, 'r') as file:
    schp.geo_data = file.readlines()

schp.surface_bc, schp.root_name = schp.get_boundary_conditions_and_root(
    schp.geo_data)
schp.n_bcs = len(set(schp.surface_bc))
root_univ = openmc.Universe(name=schp.root_name)
schp.universe_dict[schp.root_name] = root_univ

for line in schp.geo_data:
    # Create openmc Surface objects
    # corresponding to serpent surf cards
    if re.search(schp.SURF_REGEX, line):
        surf_card = re.search(schp.SURF_REGEX, line).group(0)
        schp.construct_and_store_openmc_surface(surf_card)

    # Create openmc Cell objects
    # corresponding to serpent cell cards
    elif re.search(schp.CELL_REGEX_ALL, line):
        cell_card = re.search(schp.CELL_REGEX_ALL, line).group(
            0)  # get the cell card without comments
        if re.search(schp.CELL_REGEX2_CORE, cell_card):
            split_regex = schp.CELL_REGEX2_CORE
            cell_type = "fill"
        elif re.search(schp.CELL_REGEX3_CORE, cell_card):
            split_regex = schp.CELL_REGEX3_CORE
            cell_type = "outside"
        elif re.search(schp.CELL_REGEX1_CORE, cell_card):
            split_regex = schp.CELL_REGEX1_CORE
            cell_type = "material"
        else:
            raise ValueError("Erroneous cell card type")
        my_cell, cell_name, fill_obj, cell_region = schp.construct_openmc_cell(
            cell_card, split_regex, cell_type)
        my_cell.name = cell_name
        my_cell.fill = fill_obj
        my_cell.region = cell_region
        schp.cell_dict[cell_name] = my_cell

    # transformations
    elif re.search(schp.TRANS_REGEX, line):
        trans_card = re.search(schp.TRANS_REGEX, line).group(0)
        trans_data = trans_card.split()
        trans_object_type = trans_data[1]
        trans_object_name = trans_data[2]

        # look for transformation object type
        if trans_object_type == "U":
            trans_objects_dict = schp.cell_dict
            trans_object_names = \
                schp.universe_to_cell_names_dict[trans_object_name]
        elif trans_object_type == "S":
            trans_objects_dict = schp.surf_dict
            trans_objects_names = [schp.surf_dict[trans_object_name]]
        else:
            raise ValueError(f"Transforming objects of type \
                             {trans_object_type} is currently unsupported")

        trans_objects = []
        for name in trans_object_names:
            trans_objects += [trans_objects_dict[name]]

        # check type of transformation
        # LATTICE TRANSFORMATIONS NOT CURRENTLY SUPPORTED #
        trans_args = trans_data[3:]
        n_args = len(trans_args)
        for i in range(0, n_args):
            a = trans_args[i]
            a = float(a)
            trans_args[i] = a
        trans_types = []
        translation_args = []
        rotation_args = []
        ORD = None
        # LVL, and 'rot' transformations currently unsupported
        if n_args == 3:  # transformation
            x, y, z = tuple(trans_args)
            translation_args = [x, y, z]
            trans_types = ['translation']
        elif n_args == 7:  # transformation + rotation using angles wrt axis
            x, y, z, tx, ty, tz, ORD = tuple(trans_args)
            rotation_args = sprot.from_euler('xyz', [tx, ty, tz]).as_matrix()
            translation_args = [x, y, z]
        elif n_args == 13:  # transformation + rotation using rotation matrix
            x, y, z, a1, a2, a3, a4, \
                a5, a6, a7, a8, a9, ORD = tuple(trans_args)
            rotation_args = [[a1, a2, a3],
                             [a4, a5, a6],
                             [a7, a8, a9]]
            translation_args = [x, y, z]
        else:
            raise SyntaxError("Incorrect number of arguments or unsupported \
                              transformation type")
        if bool(ORD):
            if int(ORD) == 1:
                trans_types = ['rotation', 'translation']
            elif int(ORD) == 2:
                trans_types = ['translation', 'rotation']
            else:
                raise ValueError(f"{ORD} is an invalid value for ORD")

        transformed_objects = {}
        for trans_type in trans_types:
            if trans_type == 'translation':
                for obj in trans_objects:
                    transformed_objects[obj.name] = schp.translate_obj(
                        obj, translation_args)
            elif trans_type == 'rotation':
                for obj in trans_objects:
                    transformed_objects[obj.name] = schp.rotate_obj(
                        obj, rotation_args)

        for obj_name in transformed_objects:
            trans_objects_dict[obj_name] = transformed_objects[obj_name]

    # lattices
    elif re.search(schp.LAT_REGEX, line):
        lat_card = re.search(schp.LAT_REGEX, line).group(0)
        lat_data = lat_card.split()
        lat_universe_name = lat_data[1]
        lat_type = lat_data[2]
        lat_args = lat_data[3:]

        if not bool(schp.universe_dict.get(lat_universe_name)
                    ) and lat_universe_name != schp.root_name:
            schp.universe_dict[lat_universe_name] = openmc.Universe(
                name=lat_universe_name)

        # get lattice universe array
        current_line_idx = schp.geo_data.index(line)
        lattice_origin, \
            lattice_pitch, \
            lattice_univ_array = schp.get_lattice_univ_array(lat_type,
                                                             lat_args,
                                                             current_line_idx)

        lattice_object = schp.geo_dict["lat"][lat_type](name=lat_universe_name)
        if isinstance(lattice_object, openmc.Lattice):
            if re.search("(1|6|11)", lat_type):
                lattice_object.lower_left = lattice_origin
            elif re.search("(2|3|7|8|12|13)", lat_type):
                lattice_object.center = lattice_origin
            else:
                raise ValueError("Unsupported lattice type")

            lattice_object.pitch = lattice_pitch
            lattice_object.universes = lattice_univ_array
        elif isinstance(lattice_object, openmc.Universe):
            # add cells to the universe
            if bool(schp.universe_dict[lattice_universe_name]):
                lattice_object = schp.universe_dict[lattice_universe_name]
            else:
                # lattice needs to be instantiated
                lattice_object.name = lattice_universe_name
                schp.universe_dict[lattice_universe_name] = lattice_object

            # get lattice cells...
            lattice_cells = []
            for univ in lattice_uni_array:
                cells_dict = univ.cells
                for cell_id, cell in cells_dict:
                    lattice_cells += [cell]

            lattice_object.add_cells(lattice_cells)

        # , region=universe_dict[lat_universe_name])
        lattice_cell = openmc.Cell(fill=lattice_object)
        lattice_cell.name = lat_universe_name
        schp.cell_dict[lat_universe_name] = lattice_cell
        schp.add_cell_name_to_universe(lat_universe_name, lattice_cell.name)

    # universe symmetry
    elif re.search(schp.USYM_REGEX, line):
        usym_card = re.search(schp.USYM_REGEX, line)
        usym_data = usym_card.split()
        usym_universe_name = usym_data[2]
        usym_axis = usym_data[3]
        usym_bc = usym_data[4]
        usym_xcoord = usym_data[5]
        usym_ycoord = usym_data[6]
        usym_azimuth_pos = usym_data[7]
        usym_width_ang = usym_data[8]
        usym_args = usym_data[9:]

        ...  # look into symmetries in openmc
        # otherwise we have a lot of processing to do
        # alternativley we can just use hte same BC on a plane object.


for universe_name in schp.universe_to_cell_names_dict:
    universe = schp.universe_dict[universe_name]
    cells = schp.universe_to_cell_names_dict[universe_name]
    uni_cells = []
    for cell in cells:
        uni_cells += [schp.cell_dict[cell]]
    universe.add_cells(uni_cells)
    schp.universe_dict[universe_name] = universe

root_univ = schp.universe_dict[schp.root_name]
# there's osmething not working with the cells and root universe right now
# Ill need to look into it.
# make dict of cell ids to cell obj
#all_cells = []
# for cell_name in cell_dict:
#    cell = cell_dict[cell_name]
#    all_cells += [cell]
# root_univ.add_cells(all_cells)
openmc_geometry = openmc.Geometry()
openmc_geometry.root_universe = root_univ
print(f"Root universe name: {schp.root_name}")
print(f"Root universe id: {root_univ.id}")
openmc_geometry.export_to_xml(os.path.join(path, fname + '.xml'))
