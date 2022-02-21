import re
import os
import sys
from pyne import nucname as pyname
import openmc

geo_dict = {
    "surf": {
        "inf": "",
        "px": openmc.XPlane(),
        "py": openmc.YPlane(),
        "pz": openmc.ZPlane(),
        "plane": openmc.Plane(),
        "cylx": openmc.XCylinder,
        "cyly":, openmc.YCylinder,
        "cylz": openmc.ZCylinder,
        "cyl": openmc.ZCylinder,
        "cylv": "", #emulate with region rotation
        "sph": openmc.Sphere(),
        "cone": openmc.ZCone(),
        "quadratic": openmc.Quadric(),
        "torx": openmc.XTorus(),
        "tory": openmc.YTorus(),
        "torz": openmc.ZTorus()
    }
    "cell": openmc.Cell(),
}

param_index_dict = {
    "surf": {
        "px": (3),
        "py": (3),
        "pz": (3),
        "plane": {
            7: (3, 4, 5, 6)
        } # need to throw error if there are more args than 7
        "cylx": (3, 4, 5),
        "cyly": (3, 4, 5),
        "cylz": (3, 4, 5),
        "cyl": (3, 4, 5),
        "cylv":  , #emulate with region roation
        "sph": (3, 4, 5, 6),
        "cone": (3, 4, 5, 6, 7), # partially in openmc, can emulate fully with region transformation
        "quadratic": (3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
        "torx": (3, 4, 5, 6, 7, 8),
        "tory": (3, 4, 5, 6, 7, 8),
        "torz": (3, 4, 5, 6, 7, 8)
    }
    "cell": ()
}

try:
    serpent_geot_path = str(sys.argv[1])
except IndexError:
    raise SyntaxError("No file specified")

fname = serpent_geo_path.split('/').pop(-1).split('.')[0]
path = os.path.dirname(serpent_geo_path)

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

