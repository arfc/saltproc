import re
import os
import sys
from pyne import nucname as pyname
import openmc

geo_dict = {
    "surf": {
        "inf": "",
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
SURF_REGEX=COMMENT_IGNORE_BEG_REGEX + \
    "surf\s+[a-zA-Z0-9]+\s+[a-z]{2,}(\s+[0-9]+(\.[0-9]+)?\s*)*" + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX1 = COMMENT_IGNORE_BEG_REGEX + \
    "cell(\s+[a-zA-Z0-9]+){4,}" + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX2 = COMMENT_IGNORE_BEG_REGEX + \
    "cell(\s+[a-zA-Z0-9]+){2}\s+fill(\s+\-*\:*\#*[a-zA-Z0-9]+)+" + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX3 = COMMENT_IGNORE_BEG_REGEX + \
    "cell(\s+[a-zA-Z0-9]+){2}\s+outside(\s+[a-zA-Z0-9]+)+" + \
    COMMENT_IGNORE_END_REGEX
TRANS_REGEX = COMMENT_IGNORE_BEG_REXEX

surf_dict = {} # surf name to surface object
cell_dict = {} # cell name  to cell object
universe_to_cell_dict = {}
universe_dict = {}

openmc_geometry = openmc.Geometry([])


def _construct_region_helper(cell_line, cell_type):
    """Creates input for use in openmc.Region.from_expression

    Parameters
    ----------
    cell_line : str
        A string representing a serpent `cell` card
    cell_type :
        A string representing the type of cell. Can be
        `'material'`, `'fill'`, or `'outside'`

    Returns
    -------
    my_expression : str
        Boolean expression relating surface half-spaces. Should match
        `expression` in openmc.Region.from_expression
    my_surf_dict : dict of int to openmc.Surface
        Dictionary relating surface IDs to openmc.Surface objects. Should
        match `surfaces` in openmc.Region.from_expression
    """
    # Currently only implementing 'fill' type cell
    if cell_type == 'material':
        my_line = re.search(CELL_REGEX1, cell_line).group(0)
        cell_line_splitter = "cell(\s+[a-zA-Z0-9]+){3}\s+"
    elif cell_type == 'fill':
        my_line = re.search(CELL_REGEX2, cell_line).group(0)
        cell_line_splitter = cell_type
    else:
        raise ValueError("Incorrect cell type")

    line_data = my_line.split()
    my_surf_dict = {}
    surf_name_to_surf_id = {}
    my_region_surfaces = line_data[4:] # all cell types surface data is in the same place
    # construct my_surf_dict
    for s in my_region_surfaces:
        surf_name = s.strip(" ")
        surf_name = surf_name.strip("-")
        surf_name = surf_name.strip(":")
        openmc_surf = surf_dict[surf_name]
        surf_id = openmc_surf.id
        my_surf_dict[surf_id] = openmc_surf
        surf_name_to_surf_id[openmc_surf.name] = str(surf_id)

    #construct my_expression
    if cell_type == 'material':
        my_expression = re.search(cell_line_splitter,my_line) # match object
        split_index = my_expression.span()[-1]
        my_expression = my_line[split_index:]
    else:
        my_expression = my_line.split(cell_line_splitter)[-1]
    # replace operators
    my_expression = my_expression.replace(":", "|")
    my_expression = my_expression.replace("#", "~")
    for surf_name in surf_name_to_surf_id:
        my_expression = my_expression.replace(surf_name,
                                              surf_name_to_surf_id[surf_name])
    return my_expression, my_surf_dict

for line in geo_data:
    # Create openmc Surface objects
    if re.search(SURF_REGEX, line):
        line_data = line.split()
        my_openmc_surf = geo_dict['surf'][line_data[2]].copy()
        ## addflow control for special cases
        # inf
        # plane
        first_param_index = param_index_list['surf'][line_data[2]][0]
        last_param_index = param_index_list['surf'][line_data[2]][1]
        my_params = line_data[first_param_index:last_param_index+1]
        for i in range(0,len(my_params)):
            p = float(my_params[i])
            my_params[i] = p
        my_params = tuple(my_params)
        my_openmc_surf = my_openmc_surf(my_params)
        my_openmc_surf.name = line_data[1]
        surf_dict[line_data[1]] = my_openmc_surf

    # Create openmc Cell objects
    elif re.search(CELL_REGEX1, line):
        line_data = line.split()
        cell_type = "material"
        my_expression, my_region_surfaces = _construct_region_helper(line, cell_type)
        my_region = openmc.Region.from_expression(my_expression, my_region_surfaces)

        my_cell_args = {
            "name": line_data[1],
            "fill": mat_dict[line_data[3]],
            "region": my_region
        }

        my_openmc_cell = openmc.Cell(**my_cell_args)
        cell_dict[line_data[1]] = my_openmc_cell
        if bool(universe_to_cell_dict.get(line_data[2])):
            universe_to_cell_dict[line_data[2]][line_data[1]] = my_openmc_cell
        else:
            universe_to_cell_dict[line_data[2]] = { line_data[1]: my_openmc_cell }



    # fill cell
    elif re.search(CELL_REGEX2, line):
        line_data = line.split()
        cell_type = "fill"
        my_expression, my_region_surfaces = _construct_region_helper(line, cell_type)
        my_region = openmc.Region.from_expression(my_expression, my_region_surfaces)

        my_cell_args = {
            "name": line_data[1],
            "fill": mat_dict[line_data[3]],
            "region": my_region
        }

        my_openmc_cell = openmc.Cell(**my_cell_args)
        cell_dict[line_data[1]] = my_openmc_cell
        if bool(universe_to_cell_dict.get(line_data[2])):
            universe_to_cell_dict[line_data[2]][line_data[1]] = my_openmc_cell
        else:
            universe_to_cell_dict[line_data[2]] = { line_data[1]: my_openmc_cell }


        my_cell_args = {
            "name": line_data[1],
            "fill":
        }

    elif re.search(CELL_REGEX3, line):
