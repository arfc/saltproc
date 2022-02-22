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
    "cell(\s+[a-zA-Z0-9]+){2}\s+fill(\s+[a-zA-Z0-9]+){2,}" + \
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
for line in geo_data:
   line_data = line.split()
    if re.search(SURF_REGEX, line):
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

    elif re.search(CELL_REGEX1, line):
        my_region = ...
        my_cell_args = {
            "name": line_data[1],
            "fill": mat_dict[line_data[3]],
            "region":
        }
        my_openmc_cell = openmc.Cell(**my_cell_args)
        cell_dict[line_data[1]] = my_openmc_cell
        if bool(universe_to_cell_dict.get(line_data[2])):
            universe_to_cell_dict[line_data[2]][line_data[1]] = my_openmc_cell
        else:
            universe_to_cell_dict[line_data[2]] = { line_data[1]: my_openmc_cell }

    elif re.search(CELL_REGEX2, line):
        my_cell_args = {
            "name": line_data[1],
            "fill":
        }

    elif re.search(CELL_REGEX3, line):
