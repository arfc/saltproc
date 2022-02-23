import re
import os
import sys
from pyne import nucname as pyname
import openmc

geo_dict = {
    "surf": {
        "px": openmc.XPlane,
        "py": openmc.YPlane,
        "pz": openmc.ZPlane,
        "plane": openmc.Plane,
        "cylx": openmc.XCylinder,
        "cyly":, openmc.YCylinder,
        "cylz": openmc.ZCylinder,
        "cyl": openmc.ZCylinder,
        "cylv": "", #emulate with region rotation
        "sph": openmc.Sphere,
        "cone": openmc.ZCone,
        "quadratic": openmc.Quadric,
        "torx": openmc.XTorus,
        "tory": openmc.YTorus,
        "torz": openmc.ZTorus
    },
    "cell": openmc.Cell,
    "lat": {
        "1": openmc.RectLattice,
        "2": openmc.HexLattice,
        "3": openmc.HexLattice ## ADD SUPPORT FOR MORE LATTICE TYPES
    }
}
# based on openmc.Region.from_expression()
region_operator_dict = {
    " ": " ", # intersection
    "-": "-", # complement
    "#": "~", # cell complement? unsuppored
    ":": "|", # union
}

param_index_dict = {
    "surf": {
        "px": (3),
        "py": (3),
        "pz": (3),
        "plane": {
            7: (3,  6)
        } # need to throw error if there are more args than 7
        "cylx": (3, 5),
        "cyly": (3, 5),
        "cylz": (3, 5),
        "cyl": (3, 5),
        "cylv":  , #emulate with region roation
        "sph": (3, 6),
        "cone": (3, 7), # partially in openmc, can emulate fully with region transformation
        "quadratic": (3, 12),
        "torx": (3, 8),
        "tory": (3, 8),
        "torz": (3, 8)
    },
    "cell": {
        "base": (3, -1),
        "fill": (4, -1),
        "outside": (4, -1),
    },

}

try:
    serpent_geo_path = str(sys.argv[1])
except IndexError:
    raise SyntaxError("No geo file specified")

try:
    serpent_geo_path = str(sys.argv[2])
except IndexError:
    raise SyntaxError("No material file specified")

fname = serpent_geo_path.split('/').pop(-1).split('.')[0]
path = os.path.dirname(serpent_geo_path)
openmc_mats = openmc.Materials.from_xml(sys.argv[2])
mat_dict = {}
for mat in openmc_mats:
    mat_dict[mat.name] = mat

geo_data = []
with open(serpent_geo_path, 'r') as file:
    geo_data = file.readlines()

COMMENT_IGNORE_BEG_REGEX="^\s*[^%]*\s*"
COMMENT_IGNORE_END_REGEX="\s*[^%]*"
SURF_REGEX_CORE = "surf\s+[a-zA-Z0-9]+\s+[a-z]{2,}(\s+[0-9]+(\.[0-9]+)?\s*)*"
CELL_REGEX1_CORE = "cell(\s+[a-zA-Z0-9]+){3}"
CELL_REGEX2_CORE = "cell(\s+[a-zA-Z0-9]+){2}\s+fill\s+[a-zA-Z0-9]+"
CELL_REGEX3_CORE = "cell(\s+[a-zA-Z0-9]+){2}\s+outside\s+[a-zA-Z0-9]+"
CELL_SURFACE_REGEX = "(\s+\-*\:*\#*[a-zA-Z0-9]+)+"
TRANS_REGEX_CORE = ...

SURF_REGEX=COMMENT_IGNORE_BEG_REGEX + \
    SURF_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX1 = COMMENT_IGNORE_BEG_REGEX + \
    CELL_REGEX1_CORE + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX2 = COMMENT_IGNORE_BEG_REGEX + \
    CELL_REGEX2_CORE + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX3 = COMMENT_IGNORE_BEG_REGEX + \
    CELL_REGEX3_CORE + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX_ALL = COMMENT_IGNORE_BEG_REGEX + \
    f"({CELL_REGEX2_CORE}|{CELL_REGEX3_CORE}|{CELL_REGEX1_CORE})" + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX

TRANS_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    TRANS_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX

special_case_surf_tuple = tuple(['inf'])
special_case_surf_dict = {}
surf_dict = {} # surf name to surface object
cell_dict = {} # cell name to cell object
universe_to_cell_names_dict = {}
universe_dict = {}

openmc_geometry = openmc.Geometry([])

def _construct_cell_helper(cell_card, cell_card_splitter, cell_type):
    """Helper function for creating cells

    Parameters
    ----------
    cell_card : str
        A string representing a serpent `cell` card
    cell_card_splitter : str
        A regular expresion used for extracting the surface data
        from the rest of the cell card.
    cell_type :
        A string representing the type of cell. Can be
        `'material'`, `'fill'`, or `'outside'`

    Returns
    -------
    my_cell : openmc.Cell object
        An openmc.Cell object corresponding to a Serpent cell card
    cell_name : str
        The name of the cell
    fill_obj : openmc.Material, openmc.Universe, or None
        Object to fill the cell. Variable type of fill_obj depends
        on the value of cell_type:
            'material' -> openmc.Material
            'fill' -> openmc.Universe
            'outside' -> ???
    cell_region : openmc.Region or None
        Region assigned to the cell. Can be None in certain special
        cases (e.g. declaring material cell using the complement of an
        `inf` surface)
    """

    cell_data = cell_card.split()

    cell_name = cell_data[1]
    cell_universe_name = cell_data[2]
    cell_fill_obj_name = cell_data[3]
    cell_surface_names = cell_data[4:] # all cell types surface data is in the same place
    # store universe-cell mapping for later
    if bool(universe_to_cells_dict.get(cell_universe_name)):
        universe_to_cell_names_dict[cell_universe_name] += [cell_name]
    else:
        universe_to_cell_names_dict[cell_universe_name] = [cell_name]
        universe_dict[cell_universe_name] = openmc.Universe(name=cell_universe_name)

    cell_surf_dict = {}
    surf_name_to_surf_id = {}
    my_expression = ""

    my_cell = openmc.Cell()
    fill_obj = None
    cell_region = None

    if cell_type == 'fill':
        filling_universe_name = cell_fill_obj_name
        if not bool(universe_dict.get(filling_universe_name)):
            universe_dict[filling_universe_name] = openmc.Universe(name=filling_universe_name)
        fill_obj = universe_dict[filling_universe_name]
    elif cell_type == 'outside':
        ...
    # this is messy but should work for now
    # we can clean it up later
    # Handle material cells in a null region
     if cell_type == 'material' and \
            surface_object == "inf" and \
            len(cell_surface_names) == 0:
        mat_null_cell = openmc.Cell()
        fill_obj = mat_dict[cell_fill_obj_name]
        my_cell = mat_null_cell
     else:
        # construct my_surf_dict
        skip_expression_processing = False
        for n in cell_surface_names:
            surf_name = n.strip(" ")
            surf_name = surf_name.strip("-")
            surf_name = surf_name.strip(":")
            surface_object = surf_dict[surf_name]
            surf_id = surface_object.id
            cell_surf_dict[surf_id] = surface_object
            surf_name_to_surf_id[openmc_surf.name] = str(surf_id)

        #construct my_expression
        my_expression = re.split(cell_card_splitter, cell_card)[-1]
        # replace operators
        my_expression = my_expression.replace(":", "|")
        my_expression = my_expression.replace("#", "~")
        for surf_name in surf_name_to_surf_id:
            my_expression = my_expression.replace(surf_name,
                                                  surf_name_to_surf_id[surf_name])
        cell_region = openmc.Region.from_expression(my_expression, cell_surf_dict)
    return my_cell, cell_name, fill_obj, cell_region


def _construct_surface_helper(surf_card):
    """
    Helper function for creatin `openmc.Surface` objects
    corresponding to Serpent `surf` cards

    Parameters
    ----------
    surf_card : str
        A string containing a Serpent `surf` card

    """
    surf_data = surf_card.split()
    surface_type = surf_data[2]
    surface_name = surf_data[1]

    # handle special cases
    if (special_case_surf_tuple.count(surface_type)):
        if surface_type == "inf":
            surf_dict[surface_name] = "inf" # We'll replace this later
      #  elif surface_type == "plane":
      #  elif surface_type == "cylv":


    elif bool(geo_dict['surf'].get(surface_type)): # generic cases
        my_openmc_surface = geo_dict['surf'][surface_type].copy()
        first_param_index = param_index_list['surf'][surface_type][0]
        last_param_index = param_index_list['surf'][surface_type][1]
        surface_params = surf_data[first_param_index:last_param_index+1]
        for i in range(0,len(surface_params)):
            p = float(surface_params[i])
            surfce_params[i] = p
        my_openmc_surface = my_openmc_surface(surface_params)
        my_openmc_surface.name = surface_name
        surf_dict[surface_name] = my_openmc_surf
    else:
        raise ValueError("Unsupported or erroneous surface type")



for line in geo_data:
    # Create openmc Surface objects
    # corresponding to serpent surf cards
    if re.search(SURF_REGEX, line):
        _construct_surface_helper(line)

    # Create openmc Cell objects
    # corresponding to serpent cell cards
    elif re.search(CELL_REGEX_ALL, line):
        cell_card = re.search(CELL_REGEX_ALL, line).group(0) # get the cell card without comments
        if re.search(CELL_REGEX2_CORE, cell_card):
            split_regex = CELL_REGEX2_CORE
            cell_type = "fill"
        elif re.search(CELL_REGEX3_CORE, cell_card):
            split_regex = CELL_REGEX3_CORE
            cell_type = "outside"
        elif re.search(CELL_REGEX1_CORE, cell_card):
            split_regex = CELL_REGEX1_CORE
            cell_type = "material"
        else:
            raise ValueError("Erroneous cell card type")
        my_cell, cell_name, fill_obj, cell_region = _construct_region_helper(cell_card, split_regex, cell_type)
        my_cell.name = cell_name
        my_cell.fill = fill_obj
        my_cell.region = cell_region
        cell_dict[cell_name] = my_cell


    # transformations
    elif re.search(TRANSFORMATION_REGEX, line):
        trans_data = line.split()
        trans_object_type = trans_data[1]
        trans_object_name = trans_data[2]

        # look for transformation object type
        if trans_object_type == "U":
            trans_objects_dict = cell_dict
            trans_object_names = universe_to_cell_names_dict[trans_object_name]
        elif trans_type == "S":
            trans_objects_dict = surf_dict
            trans_objects_names = [surf_dict[trans_object_name]]
        else:
            raise ValueError(f"{trans_type} is currently unsupported")

        trans_objects = []
        for name in trans_object_names:
            trans_objects += [trans_objects_dict[name]]

        # check type of transformation
        ### lattice transformations not currently supported ###
        trans_args = trans_data[3:]
        n_args = len(trans_args)
        trans_type = []
        translation_args = []
        rotation_args = []
        if n_args == 1: # LVL transformation
        elif n_args == 3: # transformation
            ...
        elif n_args == 7: # transformation + rotation using angles wrt axis
            ...
        elif n_args == 13: # transformation + rotation using rotation matrix
            ...
        else:
            raise SyntaxError("Incorrect number of arguments")

        rotation_args = tuple(rotation_args)
        translation_args = tuple(translation_args)

        transformed_objects = {}
        for trans_type in trans_types:
            if trans_type == 'translation':
                for obj in trans_objects:
                    transformed_objects[obj.name] = obj.translate(translation_args)
            elif trans_type == 'rotation':
                for obj in trans_objects:
                    transformed_objects[obj.name] = obj.rotate(rotation_args)

        for obj_name in transformed_objects:
            trans_objects_dict[obj_name] = transformed_objects[obj_name]

    elif re.search(LATTICE_REGEX, line):
        lat_data = line.split()
        lat_universe = lat_data[1]
        lat_type = lat_data[2]
        lat_args = lat_data[3:]

        # chech if all args are on one line
        current_line_idx = geo_data.index(line)
        offline_lattice_args_exist, offline_lattice_args_list = _check_for_offline_lattice_args(current_line_idx):
        if offline_lattice_args_exist: # to implement
            lat_args += office_lattice_args_list

        # flow control for different lattice types
        if lat_type == 1:
            ...
        else:
            raise ValueError(f"Type {lat_type} lattices are currently unsupported")
