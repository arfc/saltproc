import re
import os
import sys
import numpy as np
from scipy.spatial.transform import Rotation as sprot
import openmc
import openmc.model
import collections

COMMENT_IGNORE_BEG_REGEX="^\s*[^%]*\s*"
COMMENT_IGNORE_END_REGEX="\s*[^%]*"
BC_REGEX_CORE = "set\s+bc(\s+([1-3]|black|reflective|periodic)){1,3}"
SURF_REGEX_CORE = "surf\s+[a-zA-Z0-9]+\s+[a-z]{2,}(\s+[0-9]+(\.[0-9]+)?\s*)*"
CELL_REGEX1_CORE = "cell(\s+[a-zA-Z0-9]+){3}"
CELL_REGEX2_CORE = "cell(\s+[a-zA-Z0-9]+){2}\s+fill\s+[a-zA-Z0-9]+"
CELL_REGEX3_CORE = "cell(\s+[a-zA-Z0-9]+){2}\s+outside"
CELL_SURFACE_REGEX = "(\s+\-?\:?\#?[a-zA-Z0-9]+)+"
ROOT_REGEX_CORE = "set\s+root\s+[a-zA-Z0-9]+"
USYM_REGEX_CORE = "set\s+usym\s+[a-zA-Z0-9]+\s+(1|2|3)\s+(\s+-?[0-9]+(\.[0-9]+)?)"
TRANS_REGEX_CORE = "trans\s+[A-Z]{1}\s+[a-zA-Z0-9]+(\s+-?[0-9]+(\.[0-9]+)?)+"
CARD_IGNORE_REGEX = "^\s*(?!.*%)(?!.*lat)(?!.*cell)(?!.*set)(?!.*surf)(?!.*dtrans)(?!.*ftrans)(?!.*ltrans)(?!.*pin)(?!.*solid)(?!.*strans)(?!.*trans)"
LAT_REGEX_CORE = "lat\s+[a-zA-Z0-9]+\s+[0-9]{1,2}(\s+-?[0-9]+(\.[0-9]+)?){2,4}(\s+[0-9]+){0,3}((\s+-?[0-9]+(\.[0-9]+)?){0,2}\s+[a-zA-Z0-9]+)+"
LAT_MULTILINE_REGEX_CORE = "([a-zA-Z0-9]{1,3}\s+)+" # right now this is limiting universe names to 3 chars until I can come up witha more robust regex
BC_REGEX=COMMENT_IGNORE_BEG_REGEX + \
    BC_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
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
ROOT_REGEX=COMMENT_IGNORE_BEG_REGEX + \
    ROOT_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
USYM_REGEX=COMMENT_IGNORE_BEG_REGEX + \
    USYM_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX

TRANS_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    TRANS_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
LAT_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    LAT_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
LAT_MULTILINE_REGEX = CARD_IGNORE_REGEX + \
    LAT_MULTILINE_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX


geo_dict = {
    "surf": {
        "px": openmc.XPlane,
        "py": openmc.YPlane,
        "pz": openmc.ZPlane,
        "plane": openmc.Plane,
        "cylx": openmc.XCylinder,
        "cyly": openmc.YCylinder,
        "cylz": openmc.ZCylinder,
        "cyl": openmc.ZCylinder,
        "cylv": openmc.model.cylinder_from_points,
        "sph": openmc.Sphere,
        "cone": openmc.ZCone, # to implement
        "quadratic": openmc.Quadric,
        "torx": openmc.XTorus,
        "tory": openmc.YTorus,
        "torz": openmc.ZTorus,
        "sqc": openmc.model.rectangular_prism,
        "rect": openmc.model.rectangular_prism,
        "hexxc": openmc.model.hexagonal_prism, #to implement
        "hexyc": openmc.model.hexagonal_prism,  #to implement
        "cube": openmc.model.RectangularParallelepiped,
        "cuboid": openmc.model.RectangularParallelepiped
    },
    "cell": openmc.Cell,
    "lat": {
        "1": openmc.RectLattice,    # Square lattice
        "2": openmc.HexLattice,     # X-type hexagonal lattice (y type in openmc)
        "3": openmc.HexLattice,     # Y-type hexagonal lattice (x type in openmc)
     #   "4": None,                  # Circular cluster array (address as special case)
     #   "5": None,                  # Does not exist
        "6": openmc.RectLattice,    # Same as 1 but infinite
        "7": openmc.HexLattice,     # Same as 3 but infinite
        "8": openmc.HexLattice,     # Same as 2 but infinite
     #   "9": None,                  # Vertical stack (address as special case)
     #   "10": None,                 # Does not exist
        "11": openmc.RectLattice,   # Cuboidal lattice
        "12": openmc.HexLattice,    # X-type hexagonal prism lattice
        "13": openmc.HexLattice     #  Y-type hexagonal prism lattice
     #   "14": None                  # X-type triangular lattice (address as special case)
    }
}

special_case_surfaces = tuple(['inf'])

def _get_boundary_conditions_and_root(geo_data):
    """
    Helper function that gets the serpent boundary conditions
    and root universe name

    Parameters
    ----------
    geo_data : list of str
        Lines of the geometry file

    Returns
    -------
    surface_bc : str
        String that specified the Serpent boundary condtion
        in openmc format.
    root_name : str
        String that specified the root universe name
    """
    bc_card = ''
    root_card = ''
    for line in geo_data:
        if re.search(BC_REGEX, line):
            bc_card = re.search(BC_REGEX, line).group(0)
        elif re.search(ROOT_REGEX, line):
            root_card = re.search(ROOT_REGEX, line).group(0)
        if root_card != '' and bc_card != '':
            break

    surface_bc = []
    if bc_card == '':
        surface_bc += ['vacuum']
    else:
        bc_data = bc_card.split()
        bc_data = bc_data[2:]
        for bc in bc_data:
            if bc == '1' or bc == 'black':
                surface_bc += ['vacuum']
            elif bc == '2' or bc == 'reflective':
                surface_bc += ['reflective']
            elif bc == '3' or bc == 'periodic':
                surface_bc += ['periodic']
            #elif bool(float(bc)):
            #    surface_bc += ['white'] #I'm not sure this is correct
                                        # The albedo bc in serpent
                                        # allows user to specify an
                                        # albedo, wheras the white
                                        # bc in OpenMC doesn't...
            else:
                raise ValueError(f'Boundary type {bc} is invalid')

    if root_card == '':
        root_name = '0'
    else:
        root_name = root_card.split()[2]
    return surface_bc, root_name


def _construct_surface_helper(surf_card):
    """
    Helper function for creating `openmc.Surface` objects
    corresponding to Serpent `surf` cards

    Parameters
    ----------
    surf_card : str
        A string containing a Serpent `surf` card

    """
    surf_data = surf_card.split()
    surf_name = surf_data[1]
    surf_type = surf_data[2]
    surf_args = surf_data[3:]
    surf_params = surf_args.copy()
    for i in range(0,len(surf_params)):
        p = float(surf_params[i])
        surf_params[i] = p

    # generic case
    set_attributes = True
    has_subsurfaces = False
    # handle special cases
    if bool(special_case_surfaces.count(surf_type)):
        set_attributes = False
        if surf_type == "inf":
            surface_object = "inf" # We'll replace this later
    elif bool(geo_dict['surf'].get(surf_type)):
        surface_object = geo_dict['surf'][surf_type]
        if surf_type == "plane":
            # convert 3-point form to ABCD form for
            # equation of a plane
            if len(surf_params) == 9:
                p1 = np.array([surf_params[0],
                               surf_params[3],
                               surf_params[6]])
                p2 = np.array([surf_params[1],
                               surf_params[4],
                               surf_params[7]])
                p3 = np.array([surf_params[2],
                               surf_params[5],
                               surf_params[8]])
                n = np.cross(p2 - p1, p3 - p1)
                n0 = -p1
                A = n[0]
                B = n[1]
                C = n[2]
                D = np.dot(n, n0)[0]

                surface_params = [A, B, C, D]

        elif surf_type == "cylv":
           p1 = tuple(surf_params[:3])
           p2 = tuple(surf_params[3:6])
           r = surf_params[-1]
           surface_params = [p1, p2, r]

       # elif surf_type == "cone":
       #      ...
       #     surface_params = []

        elif surf_type == "sqc":
           width = surf_params[2] * 2
           height = surf_params[2] * 2
           axis = 'z'
           origin = surf_params[:2]
           surface_params = [width, height, axis, origin]
           has_subsurfaces = True

        elif surf_type == "rect":
           width = surf_params[3] - surf_params[2]
           height = surf_params[1] - surf_params[0]
           axis = 'z'
           xc = surf_params[3] - (width/2)
           yc = surf_params[1] - (height/2)
           origin = [xc, yc]
           surface_params = [width, height, axis, origin]
           has_subsurfaces = True

       # elif surf_type == "hexxc":
       #      ...
       #     surface_params = []

       # elif surf_type == "hexyc":
       #     ...
       #     surface_params = []
        elif surf_type == "cube":
            x0 = surf_params[0]
            y0 = surf_params[1]
            z0 = surf_params[2]
            d = surf_params[3]
            org_coord = [x0,y0,z0]
            surface_params = []
            for q0 in org_coord:
                surface_params += [q0 - d]
                surface_params += [q0 + d]
        else:
            surface_params = surf_params # every other surf card type already has
                                         # the necessary parameters
    else:
        raise ValueError(f"Surfaces of type {surf_type} are currently unsupported")

    if set_attributes:
        surface_params = tuple(surface_params)
        surface_object = surface_object(*surface_params)
        surface_object.name = surf_name
        # add the id parameter to CompositeSurface properties
        if not hasattr(surface_object, 'id'):
            try:
                surface_id = int(surf_name)
            except:
                surface_id = int.from_bytes(surf_name.encode(), 'litle')
            surface_object.id = surface_id

    if has_subsurfaces:
        surface_object = surface_object.get_surfaces()
        for subsurf in surface_object:
            surface_object[subsurf].name += f"_{surf_name}_sub"
    surf_dict[surf_name] = surface_object

def _strip_csg_operators(csg_expression):
    """
    Helper function for `_construct_cell_helper`

    Parameters
    ----------
    csg_expression : str
        Serpent CSG expression for cell cards

    Returns
    -------
    surf_names : list of str
        List of surface names
    """
    csg_expression = csg_expression.replace('-',' ')
    csg_expression = csg_expression.replace(':',' ')
    csg_expression = csg_expression.replace('#',' ')
    csg_expression = csg_expression.replace('(',' ')
    csg_expression = csg_expression.replace(')',' ')
    surf_names = csg_expression.split()

    return surf_names


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
    cell_object : openmc.Cell object
        An openmc.Cell object corresponding to a Serpent cell card
    cell_name : str
        The name of the cell
    cell_fill_object : openmc.Material, openmc.Universe, or None
        Object to fill the cell. Variable type of cell_fill_object depends
        on the value of cell_type:
            'material' -> openmc.Material
            'fill' -> openmc.Universe
            'outside' -> openmc.Universe
    cell_region : openmc.Region or None
        Region assigned to the cell. Can be None in certain special
        cases (e.g. declaring material cell using the complement of an
        `inf` surface)
    """
    cell_data = cell_card.split()
    cell_name = cell_data[1]
    cell_universe_name = cell_data[2]
    cell_fill_object_name = ''

    # store universe-cell mapping for later
    if bool(universe_to_cell_names_dict.get(cell_universe_name)):
        universe_to_cell_names_dict[cell_universe_name] += [cell_name]
    else:
        universe_to_cell_names_dict[cell_universe_name] = [cell_name]
        universe_dict[cell_universe_name] = openmc.Universe(name=cell_universe_name)

    cell_object = openmc.Cell()
    cell_fill_object = None
    cell_region = None

    if cell_type == 'material':
        fill_object_name_index = 3
        arg_index = 4
        cell_fill_obj_dict = mat_dict
    else:
        if cell_type == 'fill':
            fill_object_name_index = 4
        elif cell_type == 'outside':
            fill_object_name_index = 2 # This might give us an error later when we try to run
        else:
            raise ValueError(f"cell_type: {cell_type} is erroneous")

        cell_fill_obj_dict = universe_dict
        filling_universe_name = cell_data[fill_object_name_index]
        if not bool(universe_dict.get(filling_universe_name)) and filling_universe_name != root_name:
            universe_dict[filling_universe_name] = openmc.Universe(name=filling_universe_name)

    cell_fill_object_name = cell_data[fill_object_name_index]
    cell_fill_object = cell_fill_obj_dict[cell_fill_object_name]
    csg_expression = re.split(cell_card_splitter, cell_card)[-1]
    surface_names = _strip_csg_operators(csg_expression)
    subsurface_regions = {}

    # Handle special cases #
    ########################
    # material cells in a null region
    if cell_type == 'material' and \
            len(surface_names) == 1 and \
            surf_dict[surface_names[0]] == 'inf':
        mat_null_cell = openmc.Cell()
        cell_object = mat_null_cell
    # generic case
    else:
        cell_surface_dict = {}
        surface_name_to_surface_id = {}
        for surface_name in surface_names:
            surface_object = surf_dict[surface_name]
            has_subsurfaces = False
            if type(surface_object) == collections.OrderedDict:
                has_subsurfaces = True
                subsurface_regions[surface_name] = surface_object
            else:
                surface_object = {surface_name: surface_object}
            if cell_type == 'outside':
                # hack to apply bcs to both region surfaces and regular surfaces
                # without repeating code
                for s_name in surface_object:
                    if n_bcs == 1:
                        surface_object[s_name].boundary_type = surface_bc[0]
                    # we may run into trobule here when
                    # trying to apply bcs to CompositeSurfaces
                    elif n_bcs <= 3:
                        if type(surface_object) == openmc.XPlane:
                            surface_object[s_name].boundary_type = surface_bc[0]
                        elif type(surface_object) == openmc.YPlane:
                            surface_object[s_name].boundary_type = surface_bc[1]
                        elif type(surface_object) == openmc.ZPlane:
                            surface_object[s_name].boundary_type = surface_bc[2]
                        else:
                            pass # for now, need to confurm if x,y,z
                                 # bcs are applied to cylinders and
                                 # tori in serpenton
            # store surface in the the id_to_object dict
            for s_name in surface_object:
                cell_surface_dict[surface_object[s_name].id] = surface_object[s_name]

            if has_subsurfaces:
                # write subsurfaces snippet for the csg expression
                region_expr = ''
                i = 0
                if len(surface_object) == 4:
                    for subsurf in surface_object:
                        if i == 0 or i == 2:
                            region_expr += f"+{surface_object[subsurf].id} "
                        elif i == 1 or i == 3:
                            region_expr += f"-{surface_object[subsurf].id} "
                        i += 1
                    region_expr = '(' + region_expr[:-1] + ')'

                #elif len(surface_object) == 6:
                #    ...
                else:
                    raise ValueError("There were too many subsurfaces in the region")
                surface_name_to_surface_id[surface_name] = region_expr
            else:
                surface_object = surface_object[surface_name]
                surface_name_to_surface_id[surface_name] = str(surface_object.id)

        # replace operators
        csg_expression = csg_expression.replace("\s[a-zA-Z0-9]", "\s\+[a-zA-Z0-9]")
        csg_expression = csg_expression.replace(":", "|")
        csg_expression = csg_expression.replace("#", "~")
        for surface_name in surface_names:
            if bool(subsurface_regions.get(surface_name)):
                csg_expression = csg_expression.replace(f'-{surface_name}', f'{surface_name}')
                csg_expression = csg_expression.replace(f'+{surface_name}', f'~{surface_name}')
            surf_id = surface_name_to_surface_id[surface_name]
            csg_expression = csg_expression.replace(surface_name, surf_id)
        cell_region = openmc.Region.from_expression(csg_expression, cell_surface_dict)

    return cell_object, cell_name, cell_fill_object, cell_region

def _translate_obj(obj, translation_args):
    if type(obj) == openmc.Surface:
        obj = obj.translate(translation_args)
    elif type(obj) == openmc.Cell:
        if type(obj.fill) == openmc.Universe:
            obj.translation = translation_args
        elif issubclass(type(obj.region), openmc.Region):
            obj.region = obj.region.translate(translation_args)
        else:
            raise SyntaxError('Nothing to translate.')
    else:
        raise ValueError('Translations for object of type {type(obj)} \
        are currently unsupported')

    return obj

def _rotate_obj(obj, rotation_args):
    if type(obj) == openmc.Surface:
        obj = obj.rotate(rotation_args)
    elif type(obj) == openmc.Cell:
        if type(obj.fill) == openmc.Universe:
            obj.rotation = rotation_args
        elif issubclass(type(obj.region), openmc.Region):
            obj.region = obj.region.rotate(rotation_args)
        else:
            raise SyntaxError('Nothing to rotate.')
    else:
        raise ValueError('Rotations for object of type {type(obj)} \
        are currently unsupported')
    return obj



def _check_for_multiline_lattice_univ(current_line_idx, lat_args, lat_univ_index):
    """
    Helper function that looks for multi-line lattice arguments

    Parameters
    ----------
    current_line_idx : int
        Index of the current line in the geometry file
    lat_args : list of str
        arguments for the lat card. May or may not contain
        the universe names
    lat_univ_index : int
        Index of the location of the first universe in the lattice.
        Dependent on the lattice type.

    Returns
    -------
    multiline_lattice_univ_exist : bool
        True if multi-line lattice arguments exist.
        Otherwise False
    lat_lines : `numpy.ndarray`
        numpy array containing the lattice universe names
    """
    next_line = geo_data[current_line_idx + 1]
    lat_multiline_match = re.search(LAT_MULTILINE_REGEX, next_line)
    if bool(lat_multiline_match):
        multiline_lattice_univ_exist = True
        lat_lines = []
        i = current_line_idx + 1
        while (bool(lat_multiline_match)):
               line_data = lat_multiline_match.group(0).split()
               lat_lines.append(line_data)
               i += 1
               next_line = geo_data[i]
               lat_multiline_match = re.search(LAT_MULTILINE_REGEX, next_line)
    else:
        multiline_lattice_univ_exist = False
        lat_lines = lat_args[lat_univ_index:]
        lat_lines = np.array(lat_args)

    return multiline_lattice_univ_exist, lat_lines

def _get_lattice_univ_array(lattice_type, lattice_args, current_line_idx):
    """
    Helper function that creates an array
    of universes for lattice creation

    Parameters
    ----------
    lattice_type : str
        String corresponding to the serpent lattice type
    lattice_args : list of str
        String containing the lattice parameters
    current_line_idx : int
        Index of the current line in the geometry file

    Returns
    -------
    lattice_origin : tuple of float
        The lattice origin coordinate
    lattice_pitch : tuple of float
        The lattice pitch in each dimension
    lattice_univ_array : list of list of openmc.Universe
         Array containing the lattice universes
    """

    if lat_type == '1':
            x0 = float(lat_args[0])
            y0 = float(lat_args[1])
            Nx = int(lat_args[2])
            Ny = int(lat_args[3])
            pitch = float(lat_args[4])
            lat_univ_index = 8

            lat_origin = (x0, y0)
            lattice_elements = (Nx, Ny)
            lattice_pitch = (pitch, pitch)
   ## TO IMPLEMENT ##
   # elif lat_type == 2:
   #     ...
   # elif lat_type == 3:
   #     ...
   # elif lat_type == 6:
   #     ...
   # elif lat_type == 7:
   #     ...
   # elif lat_type == 8:
   #     ...
   # elif lat_type == 11:
   #     ...
   # elif lat_type == 12:
   #     ...
   # elif lat_type == 13:
   #     ...
    else:
        raise ValueError(f"Type {lat_type} lattices are currently unsupported")

    multiline_lattice_univ_exist, lattice_lines = \
        _check_for_multiline_lattice_univ(current_line_idx, lat_args, lat_univ_index)
    if not multiline_lattice_univ_exist: # to implement
        # universe names are already in a lattice structure
        lattice_univ_name_array = np.reshape(lattice_lines,lattice_elements)

    # flip the array because serpent and openmc have opposing conventions
    # for the universe order
    lattice_univ_name_array = np.flip(lattice_lines, axis=0)

    # need to calculate the new origin
    # the procedure is different for square/rect and hex lattices
    if re.match("(1|6|11)", lattice_type): # square/rect lattice
        lattice_origin = np.empty(len(lattice_elements),dtype=float)
        for Ncoord in lattice_elements:
            index = lattice_elements.index(Ncoord)
            lattice_origin[index] = Ncoord * 0.5 * lattice_pitch[index]

   ## TO IMPLEMENT ##
   # elif re.match("(2|3|7|8|12|13)"): # hex lattice
   #     lattice_origin = ...
    else:
        raise ValueError(f"Unsupported lattice type: {lattice_type}")

    lattice_origin = tuple(lattice_origin)
    lattice_univ_array = np.empty(lattice_elements, dtype=openmc.Universe)
    for n in np.unique(lattice_univ_name_array):
        lattice_univ_array[np.where(lattice_univ_name_array == n)] = \
            universe_dict[n]

    return lattice_origin, lattice_pitch, lattice_univ_array

# Read command line input
try:
    serpent_geo_path = str(sys.argv[1])
except IndexError:
    raise SyntaxError("No geo file specified")

try:
    openmc_mat_path = str(sys.argv[2])
except IndexError:
    raise SyntaxError("No material file specified")

# get filenames
fname = serpent_geo_path.split('/').pop(-1).split('.')[0]
path = os.path.dirname(serpent_geo_path)
openmc_mats = openmc.Materials.from_xml(openmc_mat_path)
mat_dict = {}
for mat in openmc_mats:
    mat_dict[mat.name] = mat
# add void material
mat_dict['void'] = None

geo_data = []
with open(serpent_geo_path, 'r') as file:
    geo_data = file.readlines()

surface_bc, root_name= _get_boundary_conditions_and_root(geo_data) ### TO IMPLEMENT ###
n_bcs = len(set(surface_bc))
surf_dict = {} # surf name to surface object
cell_dict = {} # cell name to cell object
universe_to_cell_names_dict = {}
universe_dict = {}
root_univ = openmc.Universe(name=root_name)
universe_dict[root_name] = root_univ

for line in geo_data:
    # Create openmc Surface objects
    # corresponding to serpent surf cards
    if re.search(SURF_REGEX, line):
        surf_card = re.search(SURF_REGEX, line).group(0)
        _construct_surface_helper(surf_card)

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
        my_cell, cell_name, fill_obj, cell_region = _construct_cell_helper(cell_card, split_regex, cell_type)
        my_cell.name = cell_name
        my_cell.fill = fill_obj
        my_cell.region = cell_region
        cell_dict[cell_name] = my_cell


    # transformations
    elif re.search(TRANS_REGEX, line):
        trans_card = re.search(TRANS_REGEX,line).group(0)
        trans_data = trans_card.split()
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
            raise ValueError(f"Transforming objects of type \
                             {trans_type} is currently unsupported")

        trans_objects = []
        for name in trans_object_names:
            trans_objects += [trans_objects_dict[name]]

        # check type of transformation
        ### lattice transformations not currently supported ###
        trans_args = trans_data[3:]
        n_args = len(trans_args)
        for i in range(0,n_args):
            a = trans_args[i]
            a = float(a)
            trans_args[i] = a
        trans_types = []
        translation_args = []
        rotation_args = []
        ORD = None
        # LVL, and 'rot' transformations currently unsupported
        if n_args == 3: # transformation
            x, y, z = tuple(trans_args)
            translation_args = [x, y, z]
            trans_types = ['translation']
        elif n_args == 7: # transformation + rotation using angles wrt axis
            x, y, z, tx, ty, tz, ORD = tuple(trans_args)
            rotation_args = sprot.from_euler('xyz', [tx, ty, tz]).as_matrix()
            translation_args = [x, y, z]
        elif n_args == 13: # transformation + rotation using rotation matrix
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
                    transformed_objects[obj.name] = _translate_obj(obj,translation_args)
            elif trans_type == 'rotation':
                for obj in trans_objects:
                    transformed_objects[obj.name] = _rotate_obj(obj,rotation_args)

        for obj_name in transformed_objects:
            trans_objects_dict[obj_name] = transformed_objects[obj_name]

    # lattices
    elif re.search(LAT_REGEX, line):
        lat_card = re.search(LAT_REGEX, line).group(0)
        lat_data = lat_card.split()
        lat_universe_name = lat_data[1]
        lat_type = lat_data[2]
        lat_args = lat_data[3:]

        if not bool(universe_dict.get(lat_universe_name)) and lat_universe_name != root_name:
           universe_dict[lat_universe_name] = openmc.Universe(name=lat_universe_name)

        # get lattice universe array
        current_line_idx = geo_data.index(line)
        lattice_origin, \
            lattice_pitch, \
            lattice_univ_array = _get_lattice_univ_array(lat_type,
                                                         lat_args,
                                                         current_line_idx)

        lattice_object = geo_dict["lat"][lat_type](name=lat_universe_name)
        if re.search("(1|6|11)", lat_type):
            lattice_object.lower_left = lattice_origin
        elif re.search("(2|3|7|8|12|13)", lat_type):
            lattice_object.center = lattice_origin
        else:
            raise ValueError("Unsupported lattice type")

        lattice_object.pitch = lattice_pitch
        lattice_object.universes = lattice_univ_array
        lattice_cell = openmc.Cell(fill=lattice_object)#, region=universe_dict[lat_universe_name])
        lattice_cell.name = lat_universe_name
        cell_dict[lat_universe_name] = lattice_cell

    ## root universe
    elif re.search(ROOT_REGEX, line):
        root_name = line.split()[2]
        root_univ.name = root_name

    ## universe symmetry
    elif re.search(USYM_REGEX, line):
        usym_card = re.search(USYM_REGEX, line)
        usym_data = usym_card.split()
        usym_universe_name = usym_data[2]
        usym_axis = usym_data[3]
        usym_bc = usym_data[4]
        usym_xcoord = usym_data[5]
        usym_ycoord = usym_data[6]
        usym_azimuth_pos = usym_data[7]
        usym_width_ang = usym_data[8]
        usym_args = usym_data[9:]

        ... # look into symmetries in openmc
            # otherwise we have a lot of processing to do
            # alternativley we can just use hte same BC on a plane object.



for universe_name in universe_to_cell_names_dict:
    universe = universe_dict[universe_name]
    cells = universe_to_cell_names_dict[universe_name]
    uni_cells = []
    for cell in cells:
        uni_cells += [cell_dict[cell]]
    universe.add_cells(uni_cells)
    universe_dict[universe_name] = universe

root_univ = universe_dict[root_name]
# make dict of cell ids to cell obj
all_cells = []
for cell_name in cell_dict:
    cell = cell_dict[cell_name]
    all_cells += [cell]
root_univ.add_cells(all_cells)
openmc_geometry = openmc.Geometry()
openmc_geometry.root_universe = root_univ
print(path)
openmc_geometry.export_to_xml(os.path.join(path, fname+'.xml'))
