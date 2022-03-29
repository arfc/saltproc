import re
import numpy as np
import openmc
import openmc.model
import collections

global surf_dict, cell_dict, mat_dict, universe_dict
global universe_to_cell_names_dict
global geo_data, n_bcs
global surface_bc, root_name

surf_dict = {}
cell_dict = {}
mat_dict = {}
universe_dict = {}
universe_to_cell_names_dict = {}
geo_data = []

NUM_REGEX = '-?[0-9]+(\.[0-9]+)?'
COMMENT_IGNORE_BEG_REGEX = '^\s*[^%]*\s*'
COMMENT_IGNORE_END_REGEX = '\s*[^%]*'
BC_REGEX_CORE = 'set\s+bc(\s+([1-3]|black|reflective|periodic)){1,3}'
SURF_REGEX_CORE = 'surf\s+[a-zA-Z0-9]+\s+[a-z]{2,}(\s+' + \
    NUM_REGEX + '\s*)*'
CELL_REGEX1_CORE = 'cell(\s+[a-zA-Z0-9]+){3}'
CELL_REGEX2_CORE = 'cell(\s+[a-zA-Z0-9]+){2}\s+fill\s+[a-zA-Z0-9]+'
CELL_REGEX3_CORE = 'cell(\s+[a-zA-Z0-9]+){2}\s+outside'
CELL_SURFACE_REGEX = '(\s+\-?\:?\#?[a-zA-Z0-9]+)+'
ROOT_REGEX_CORE = 'set\s+root\s+[a-zA-Z0-9]+'
USYM_REGEX_CORE = 'set\s+usym\s+[a-zA-Z0-9]+\s+(1|2|3)\s+(\s+' + \
    NUM_REGEX + ')'
TRANS_REGEX_CORE = 'trans\s+[A-Z]{1}\s+[a-zA-Z0-9]+(\s+' + NUM_REGEX + ')+'
CARD_IGNORE_REGEX = '^\s*(?!.*%)(?!.*lat)(?!.*cell)(?!.*set)(?!.*surf)' + \
    '(?!.*dtrans)(?!.*ftrans)(?!.*ltrans)(?!.*pin)(?!.*solid)(?!.*strans)' + \
    '(?!.*trans)'
LAT_REGEX_CORE = 'lat\s+[a-zA-Z0-9]+\s+[0-9]{1,2}(\s+' + NUM_REGEX + \
    '){2,4}(\s+[0-9]+){0,3}((\s+' + NUM_REGEX + '){0,2}\s+[a-zA-Z0-9]+)+'
# right now this is limiting universe names to 3 chars until I can come up
# witha more robust regex
LAT_MULTILINE_REGEX_CORE = '\s*((' + NUM_REGEX + '\s+){0,2}[a-zA-Z0-9]{1,3}\s+)+'
BC_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    BC_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
SURF_REGEX = COMMENT_IGNORE_BEG_REGEX + \
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
    f'({CELL_REGEX2_CORE}|{CELL_REGEX3_CORE}|{CELL_REGEX1_CORE})' + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
ROOT_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    ROOT_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
USYM_REGEX = COMMENT_IGNORE_BEG_REGEX + \
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



def _plane_from_points(p1, p2, p3):
    # get plane from points p1, p2, p3
    n = np.cross(p2 - p1, p3 - p1)
    n0 = -p1
    A = n[0]
    B = n[1]
    C = n[2]
    D = np.dot(n, n0)

    return [A, B, C, D]


class Octagon(openmc.model.CompositeSurface):
    """Infinite octogonal prism composite surface

    An octagonal prism is composed of eight surfaces. The prism is parallel to
    the x, y, or z axis; two pars of surfaces are perpendicualr to the z and y,
    x and z, or y and x axes, respectively.

    This class
    acts as a proper surface, meaning that unary `+` and `-` operators applied
    to it will produce a half-space. The negative side is defined to be the
    region inside of the octogonal prism.

    Parameters
    ----------
    center : 2-tuple
        (q1,q2) coordinate for the center of the octagon. (q1,q2) pairs are
        (z,y), (x,z), or (x,y).
    r1 : float
        Half-width of octagon across axis-perpendicualr sides
    r2 : float
        Half-width of octagon across off-axis sides
    axis : char
        Central axis of ocatgon. Defaults to 'z'

    Attributes
    ----------
    top : openmc.ZPlane or openmc.XPlane
        Top planar surface of Hexagon
    bottom : openmc.ZPlane or openmc.XPlane
    right: openmc.YPlane or openmc.ZPlane
    left: openmc.YPlane or openmc.ZPlane
    upper_right : openmc.Plane
    lower_right : openmc.Plane
    lower_left : openmc.Plane
    upper_left : openmc.Plane

    """

    _surface_names = ('top', 'bottom',
                      'upper_right', 'lower_left',
                      'right', 'left',
                      'lower_right', 'upper_left')

    def __init__(self, center, r1, r2, axis='z', **kwargs):
        q1c, q2c = center

        # Coords for axis-perpendicular planes
        ctop = q1c+r1
        cbottom = q1c-r1

        cright= q2c+r1
        cleft = q2c-r1

        # Side lengths
        L_perp_ax1 = (r1 * np.sqrt(2) - r2) * 2
        L_perp_ax2 = (r2 * np.sqrt(2) - r1) * 2

        # Coords for quadrant planes
        p1_upper_right = [L_perp_ax1/2, r1,0]
        p2_upper_right = [r1, L_perp_ax1/2,0]
        p3_upper_right = [r1, L_perp_ax1/2,1]

        p1_lower_right = [r1, -L_perp_ax1/2,0]
        p2_lower_right = [L_perp_ax1/2, -r1,0]
        p3_lower_right = [L_perp_ax1/2, -r1,1]

        points = [p1_upper_right, p2_upper_right, p3_upper_right,
                  p1_lower_right, p2_lower_right, p3_lower_right]

        # Orientation specific variables
        if axis == 'x':
            coord_map = [2,1,0]
            self.top = openmc.ZPlane(z0=ctop)
            self.bottom = openmc.ZPlane(z0=cbottom)

            self.right = openmc.YPlane(y0=cright)
            self.left = openmc.YPlane(y0=cleft)

        elif axis == 'y':
            coord_map = [1,0,2]
            self.top = openmc.XPlane(x0=ctop)
            self.bottom = openmc.XPlane(x0=cbottom)
            self.right = openmc.ZPlane(z0=cright)
            self.left = openmc.ZPlane(z0=cleft)

        elif axis == 'z':
            coord_map = [0,1,2]
            self.top = openmc.XPlane(x0=ctop)
            self.bottom = openmc.XPlane(x0=cbottom)
            self.right = openmc.YPlane(y0=cright)
            self.left = openmc.YPlane(y0=cleft)


        # Put our coordinates in (x,y,z) order
        calibrated_points = []
        for p in points:
            p_temp = []
            for i in coord_map:
                p_temp += [p[i]]
            calibrated_points += [np.array(p_temp)]

        p1_upper_right, p2_upper_right, p3_upper_right,\
            p1_lower_right, p2_lower_right, p3_lower_right = calibrated_points

        upper_right_params = _plane_from_points(p1_upper_right,
                                                p2_upper_right,
                                                p3_upper_right)
        lower_right_params = _plane_from_points(p1_lower_right,
                                                p2_lower_right,
                                                p3_lower_right)
        lower_left_params = _plane_from_points(-p1_upper_right,
                                               -p2_upper_right,
                                               -p3_upper_right)
        upper_left_params = _plane_from_points(-p1_lower_right,
                                               -p2_lower_right,
                                               -p3_lower_right)

        self.upper_right = openmc.Plane(*tuple(upper_right_params))
        self.lower_right = openmc.Plane(*tuple(lower_right_params))
        self.lower_left = openmc.Plane(*tuple(lower_left_params))
        self.upper_left = openmc.Plane(*tuple(upper_left_params))


    def __neg__(self):
        return -self.top & +self.bottom & -self.right &  +self.left & \
            -self.upper_right & +self.lower_right & +self.lower_left & \
            -self.upper_left


    def __pos__(self):
        return +self.top | -self.bottom | +self.right | -self.left | \
            +self.upper_right | -self.lower_right | -self.lower_left | \
            +self.upper_left




class CylinderSector(openmc.model.CompositeSurface):
    """Infinite cylindrical sector composite surface

    This class
    acts as a proper surface, meaning that unary `+` and `-` operators applied
    to it will produce a half-space. The negative side is defined to be the
    region inside of the octogonal prism.

    Parameters
    ----------
    center : 2-tuple
        (x,y) coordiante of cylinder's central axis
    r1, r2 : float
        Inner and outer radius
    alpha1, alpha2 : float
        Angular segmentation

    Attributes
    ----------
    outer : openmc.ZCylinder
        Outer cylinder surface
    inner : openmc.ZCylinder
        Inner cylinder surface
    plane_a : openmc.Plane
    plane_b : openmc.Plane

    """

    _surface_names = ('outer','inner',
                      'plane_a', 'plane_b')

    def __init__(self, center, r1, r2, alpha1, alpha2, **kwargs):

        xc,yc = center
        # Coords for axis-perpendicular planes
        p1 = np.array([0,0,1])

        p2_plane_a = np.array([r1 * np.cos(alpha1), -r1 * np.sin(alpha1), 0])
        p3_plane_a = np.array([r2 * np.cos(alpha1), -r2 * np.sin(alpha1), 0])

        p2_plane_b = np.array([r1 * np.cos(alpha2), r1 * np.sin(alpha2), 0])
        p3_plane_b = np.array([r2 * np.cos(alpha2), r2 * np.sin(alpha2), 0])

        plane_a_params = _plane_from_points(p1, p2_plane_a, p3_plane_a)
        plane_b_params = _plane_from_points(p1, p2_plane_b, p3_plane_b)

        self.inner = openmc.ZCylinder(x0=xc, y0=yc, r=r1)
        self.outer = openmc.ZCylinder(x0=xc, y0=yc, r=r2)
        self.plane_a = openmc.Plane(*plane_a_params)
        self.plane_b = openmc.Plane(*plane_b_params)


    def __neg__(self):
        return -self.outer & +self.inner & -self.plane_a &  +self.plane_b


    def __pos__(self):
        return +self.outer | -self.inner | +self.plane_a | -self.plane_b


class HalfCone(openmc.model.CompositeSurface):
    """Finite half-cone composite surface. Parallel to z-axis

    This class
    acts as a proper surface, meaning that unary `+` and `-` operators applied
    to it will produce a half-space. The negative side is defined to be the
    region inside of the octogonal prism.

    Parameters
    ----------
    base: 3-tuple
        (x,y,z) coordiante of the point on the base and the
        cylinder's central axis
    r : float
        Base radius
    h : float
        Height

    Attributes
    ----------
    cone : openmc.ZCone
        Outer cylinder surface
    bottom : openmc.ZPlane
    top : openmc.ZPlane

    """

    _surface_names = ('cone', 'bottom', 'top')

    def __init__(self, base, r, h, **kwargs):

        xb,yb,zb = base

        self.cone = openmc.ZCone(x0=xb,y0=yb,z0=h-zb,r2=r)
        self.top = openmc.ZPlane(z0 = h-zb)
        self.bottom = openmc.ZPlane(z0=zb)


    def __neg__(self):
        return -self.cone & +self.bottom


    def __pos__(self):
        return +self.cone | -self.bottom



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
        "cone": HalfCone,  # to implement
        "quadratic": openmc.Quadric,
        "torx": openmc.XTorus,
        "tory": openmc.YTorus,
        "torz": openmc.ZTorus,
        "sqc": openmc.model.rectangular_prism,
        "rect": openmc.model.rectangular_prism,
        "hexxc": openmc.model.hexagonal_prism,
        "hexyc": openmc.model.hexagonal_prism,
        "cube": openmc.model.RectangularParallelepiped,
        "cuboid": openmc.model.RectangularParallelepiped,
        "octa": Octagon,
        "pad": CylinderSector
    },
    "cell": openmc.Cell,
    "lat": {
        "1": openmc.RectLattice,    # Square lattice
        "2": openmc.HexLattice,  # X-type hexagonal lattice (y type in openmc)
        "3": openmc.HexLattice,  # Y-type hexagonal lattice (x type in openmc)
        #   "4": None,     # Circular cluster array (address as special case)
        "6": openmc.RectLattice,    # Same as 1 but infinite
        "7": openmc.HexLattice,     # Same as 3 but infinite
        "8": openmc.HexLattice,     # Same as 2 but infinite
        "9": openmc.Universe,          # Vertical stack (address as special case)
        "11": openmc.RectLattice,   # Cuboidal lattice
        "12": openmc.HexLattice,  # X-type hexagonal prism lattice
        "13": openmc.HexLattice  # Y-type hexagonal prism lattice
        #   "14": None    # X-type triangular lattice (address as special case)
    }
}

special_case_surfaces = tuple(['inf'])

def add_cell_name_to_universe(univ_name,
                              cell_name):
    """
    univ_name : str
        Name of the universe
    cell_name : str
        Cell name to add to the universe
    """
    if bool(universe_to_cell_names_dict.get(univ_name)):
        universe_to_cell_names_dict[univ_name] += [cell_name]
    else:
        universe_to_cell_names_dict[univ_name] = [cell_name]
        universe_dict[univ_name] = openmc.Universe(name=univ_name)


def get_boundary_conditions_and_root(geo_data):
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
            if bc in ('1', 'black'):
                surface_bc += ['vacuum']
            elif bc in ('2', 'reflective'):
                surface_bc += ['reflective']
            elif bc in ('3', 'periodic'):
                surface_bc += ['periodic']
            # elif bool(float(bc)):
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


def _get_openmc_surface_params(surf_type,
                               surf_params):
    # generic case
    surface_params = None
    set_attributes = True
    has_subsurfaces = False
    # handle special cases
    if bool(special_case_surfaces.count(surf_type)):
        set_attributes = False
    elif bool(geo_dict['surf'].get(surf_type)):
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
                surface_params = _plane_from_points(p1, p2, p3)
            else:
                surface_params = surf_params

        elif surf_type == "cylv":
            p1 = tuple(surf_params[:3])
            p2 = tuple(surf_params[3:6])
            r = surf_params[-1]
            surface_params = [p1, p2, r]

        elif surf_type == "cone":
            base = tuple(surf_params[:3])
            r = surf_params[3]
            h = surf_params[4]
            surface_params = [base, r, h]
            has_subsurfaces = True

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
            xc = surf_params[3] - (width / 2)
            yc = surf_params[1] - (height / 2)
            origin = [xc, yc]
            surface_params = [width, height, axis, origin]
            has_subsurfaces = True

        elif surf_type in ("hexxc", "hexyc"):
            x0 = surf_params[0]
            y0 = surf_params[1]
            d = surf_params[2]

            edge_length = 2 * d / np.sqrt(3)
            if surf_type == "hexxc":
                orientation = 'y'
            else:
                orientation = 'x'

            origin = (x0, y0)
            surface_params = [edge_length, orientation, origin]
            has_subsurfaces = True

        elif surf_type == "cube":
            x0 = surf_params[0]
            y0 = surf_params[1]
            z0 = surf_params[2]
            d = surf_params[3]
            org_coord = [x0, y0, z0]
            surface_params = []
            for q0 in org_coord:
                surface_params += [q0 - d]
                surface_params += [q0 + d]
            has_subsurfaces = True

        elif surf_type == "octa":
            x0 = surf_params[0]
            y0 = surf_params[1]
            d1 = surf_params[2]
            d2 = surf_params[3]

            origin = (x0, y0)
            surface_params = [origin, d1, d2, 'z']
            has_subsurfaces=True

        elif surf_type == "pad":
            x0 = surf_params[0]
            y0 = surf_params[1]
            r1 = surf_params[2]
            r2 = surf_params[3]
            a1 = surf_params[4]
            a2 = surf_params[5]

            origin = (x0, y0)
            surface_params = [origin, r1, r2, a1, a2]
            has_subsurfaces=True

        else:
            surface_params = surf_params    # every other surf card type
                                            # already  has the necessary
                                            # parameters
    else:
        raise ValueError(
            f"Surfaces of type {surf_type} are currently unsupported")

    return surface_params, set_attributes, has_subsurfaces


def construct_and_store_openmc_surface(surf_card):
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
    for i, p in enumerate(surf_params):
        p = float(p)
        surf_params[i] = p

    surface_params, set_attributes, has_subsurfaces = \
        _get_openmc_surface_params(surf_type, surf_params)

    if surface_params is None:
        surface_object = surf_type
    else:
        surface_object = geo_dict['surf'][surf_type]

    if set_attributes:
        surface_params = tuple(surface_params)
        surface_object = surface_object(*surface_params)
        if isinstance(surface_object, openmc.model.CompositeSurface):
            surface_object = -surface_object
        surface_object.name = surf_name
        # add the id parameter to CompositeSurface properties
        if not hasattr(surface_object, 'id'):
            try:
                surface_id = int(surf_name)
            except BaseException:
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
    csg_expression = csg_expression.replace('-', ' ')
    csg_expression = csg_expression.replace(':', ' ')
    csg_expression = csg_expression.replace('#', ' ')
    csg_expression = csg_expression.replace('(', ' ')
    csg_expression = csg_expression.replace(')', ' ')
    surf_names = csg_expression.split()

    return surf_names


def _get_subsurf_region_expr_helper(subsurf_names,
                                    subsurf_dict,
                                    match_pos_hs,
                                    match_neg_hs):
    region_expr = ''
    for i, subsurf_name in enumerate(subsurf_names):
        subsurf_id = subsurf_dict[subsurf_name].id
        if match_pos_hs(i):
            region_expr += f"+{subsurf_id} "
        elif match_neg_hs(i):
            region_expr += f"-{subsurf_id} "
        else:
            raise ValueError("Bad index when creating csg \
                             expression for subsurfaces")
    return region_expr


def _get_subsurf_region_expr(subsurf_dict):
    subsurf_names = list(subsurf_dict)
    n_surfs = len(subsurf_dict)
    if n_surfs == 2: #cone
        match_pos_hs = lambda i : i in (1,)
        match_neg_hs = lambda i : i in (0,)
    elif n_surfs == 4:  # rect
        match_pos_hs = lambda i : i in (0, 2)
        match_neg_hs = lambda i : i in (1, 3)
    elif n_surfs == 6:  # hex
        if isinstance(subsurf_dict[subsurf_names[0]], openmc.XPlane):
            match_pos_hs = lambda i : i in (0, 2, 3)
            match_neg_hs = lambda i : i in (1, 4, 5)
        elif isinstance(subsurf_dict[subsurf_names[0]], openmc.YPlane):
            match_pos_hs = lambda i : i in (0, 2, 5)
            match_neg_hs = lambda i : i in (1, 4, 3)
    elif n_surfs == 8: #octagon
        match_pos_hs = lambda i : i in (1,3,5,6)
        match_neg_hs = lambda i : i in (0,2,4,7)
    else:
        raise ValueError("There were too many \
                         subsurfaces in the region")

    region_expr = _get_subsurf_region_expr_helper(subsurf_names,
                                                  subsurf_dict,
                                                  match_pos_hs,
                                                  match_neg_hs)
    region_expr = '(' + region_expr[:-1] + ')'
    return region_expr


def construct_openmc_cell(cell_card,
                          cell_card_splitter,
                          cell_type):
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
    add_cell_name_to_universe(cell_universe_name, cell_name)

    cell_object = openmc.Cell()
    cell_fill_object = None
    cell_region = None

    if cell_type == 'outside':
        pass
    else:
        if cell_type == 'material':
            fill_object_name_index = 3
            cell_fill_obj_dict = mat_dict
        elif cell_type == 'fill':
            fill_object_name_index = 4
            cell_fill_obj_dict = universe_dict
            filling_universe_name = cell_data[fill_object_name_index]
            if not bool(universe_dict.get(filling_universe_name)
                        ) and filling_universe_name != root_name:
                universe_dict[filling_universe_name] = openmc.Universe(
                    name=filling_universe_name)
        else:
            raise ValueError(f"cell_type: {cell_type} is erroneous")

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
            if isinstance(surface_object, collections.OrderedDict):
                has_subsurfaces = True
                subsurface_regions[surface_name] = surface_object
            else:
                surface_object = {surface_name: surface_object}
            if cell_type == 'outside':
                # hack to apply bcs to both region surfaces and regular
                # surfaces without repeating code
                for s_name in surface_object:
                    if n_bcs == 1:
                        surface_object[s_name].boundary_type = surface_bc[0]
                    # we may run into trobule here when
                    # trying to apply bcs to CompositeSurfaces
                    elif n_bcs <= 3:
                        if isinstance(surface_object, openmc.XPlane):
                            surface_object[s_name].boundary_type = \
                                surface_bc[0]
                        elif isinstance(surface_object, openmc.YPlane):
                            surface_object[s_name].boundary_type = \
                                surface_bc[1]
                        elif isinstance(surface_object, openmc.ZPlane):
                            surface_object[s_name].boundary_type = \
                                surface_bc[2]
                        else:
                            pass  # for now, need to confurm if x,y,z
                            # bcs are applied to cylinders and
                            # tori in serpenton
            # store surface in the the id_to_object dict
            for s_name in surface_object:
                s_id = surface_object[s_name].id
                cell_surface_dict[s_id] = surface_object[s_name]

            if has_subsurfaces:
                # write subsurfaces snippet for the csg expression
                region_expr = _get_subsurf_region_expr(surface_object)
                surface_name_to_surface_id[surface_name] = region_expr
            else:
                surface_object = surface_object[surface_name]
                surface_name_to_surface_id[surface_name] = str(
                    surface_object.id)

        # replace operators
        csg_expression = csg_expression.replace(
            "\\s[a-zA-Z0-9]", "\\s\\+[a-zA-Z0-9]")
        csg_expression = csg_expression.replace(":", "|")
        csg_expression = csg_expression.replace("#", "~")
        for surface_name in surface_names:
            if bool(subsurface_regions.get(surface_name)):
                csg_expression = csg_expression.replace(
                    f'-{surface_name}', f'{surface_name}')
                csg_expression = csg_expression.replace(
                    f'+{surface_name}', f'~{surface_name}')

        # will work on a cleaner implementation later
        csg_split_expr = csg_expression.split()
        for i, surface_name in enumerate(surface_names):
            surf_id = surface_name_to_surface_id[surface_name]
            surf_expr = csg_split_expr[i]
            csg_split_expr[i] = surf_expr.replace(surface_name, surf_id)
        csg_expression = ' '.join(csg_split_expr)
        cell_region = openmc.Region.from_expression(
            csg_expression, cell_surface_dict)

    return cell_object, cell_name, cell_fill_object, cell_region


def translate_obj(obj,
                  translation_args):
    if isinstance(obj, openmc.Surface):
        obj = obj.translate(translation_args)
    elif isinstance(obj, openmc.Cell):
        if isinstance(obj.fill, openmc.Universe):
            obj.translation = translation_args
        elif issubclass(type(obj.region), openmc.Region):
            obj.region = obj.region.translate(translation_args)
        else:
            raise SyntaxError('Nothing to translate.')
    else:
        raise ValueError('Translations for object of type {type(obj)} \
        are currently unsupported')

    return obj


def rotate_obj(obj,
               rotation_args):
    if isinstance(obj, openmc.Surface):
        obj = obj.rotate(rotation_args)
    elif isinstance(obj, openmc.Cell):
        if isinstance(obj.fill, openmc.Universe):
            obj.rotation = rotation_args
        elif issubclass(type(obj.region), openmc.Region):
            obj.region = obj.region.rotate(rotation_args)
        else:
            raise SyntaxError('Nothing to rotate.')
    else:
        raise ValueError('Rotations for object of type {type(obj)} \
        are currently unsupported')
    return obj


def _get_lattice_universe_names(current_line_idx,
                                lattice_args,
                                lat_univ_index):
    """
    Helper function that looks for the lattice universe arguments

    Parameters
    ----------
    current_line_idx : int
        Index of the current line in the geometry file
    lattice_args : list of str
        arguments for the lat card. May or may not contain
        the universe names
    lat_univ_index : int
        Index of the location of the first universe in the lattice.
        Dependent on the lattice type.

    Returns
    -------
    lat_univ_names : `numpy.ndarray`
        numpy array containing the lattice universe names
    """
    next_line = geo_data[current_line_idx + 1]
    lat_multiline_match = re.search(LAT_MULTILINE_REGEX, next_line)
    # Not sure why anyone would do this, but just to be safe
    # check the args for any universe specifications
    lat_univ_names = []
    try:
        lat_univ_names += lattice_args[lat_univ_index:]
    except IndexError:
        pass
    if bool(lat_multiline_match):
        i = current_line_idx + 1
        while (bool(lat_multiline_match)):
            line_data = lat_multiline_match.group(0).split()
            lat_univ_names.append(line_data)
            i += 1
            next_line = geo_data[i]
            lat_multiline_match = re.search(LAT_MULTILINE_REGEX, next_line)

    lat_univ_names = np.array(lat_univ_names)

    return lat_univ_names


def get_lattice_univ_array(lattice_type,
                           lattice_args,
                           current_line_idx):
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
    lattice_universe_array : `numpy.ndarray` of openmc.Universe
         Array containing the lattice universes
    """

    x0 = float(lattice_args[0])
    y0 = float(lattice_args[1])

    if re.match("(1|2|3)", lattice_type):
        Nx = int(lattice_args[2])
        Ny = int(lattice_args[3])
        pitch = float(lattice_args[4])
        lat_univ_index = 5

        lattice_origin = (x0, y0)
        lattice_elements = (Nx, Ny)
        lattice_pitch = (pitch, pitch)
    # TO IMPLEMENT
    #elif lat_type == 6:
    #    ...
    #elif lat_type == 7:
    #    ...
    #elif lat_type == 8:
    #    ...
    elif lattice_type == '9':  # vertical stack
        x0 = float(lattice_args[0])
        y0 = float(lattice_args[1])
        N_L = int(lattice_args[2])
        lat_univ_index = 4

        lattice_origin = (x0, y0)
        lattice_elements = (N_L, 2)

    #elif lat_type == 11:
    #    ...
    #elif lat_type == 12:
    #    ...
    #elif lat_type == 13:
    #    ...
    else:
        raise ValueError(
            f"Type {lattice_type} lattices are currently unsupported")

    lat_univ_names = _get_lattice_universe_names(
        current_line_idx, lattice_args, lat_univ_index)

    lattice_universe_name_array = np.reshape(lat_univ_names, lattice_elements)


    # need to calculate the new origin
    # the procedure is different for square/rect and hex lattices
    if re.match("(1|6|11)", lattice_type):  # square/rect lattice
        # flip the array because serpent and openmc have opposing conventions
        # for the universe order
        lattice_universe_name_array = np.flip(
            lattice_universe_name_array, axis=0)

        lattice_origin = np.empty(len(lattice_elements), dtype=float)

        for Ncoord in lattice_elements:
            index = lattice_elements.index(Ncoord)
            lattice_origin[index] = Ncoord * 0.5 * lattice_pitch[index]

    elif lattice_type == '9':  # vertical stack
       lattice_universe_names = lattice_universe_name_array[:,1]
       lattice_origin = list(lattice_origin)
       lattice_elements = (N_L)
       lattice_pitch = None

       for zcoord, universe_name in lattice_universe_name_array:
           cell_names = universe_to_cell_names_dict[universe_name]

           # translate the cells
           for cell_name in cell_names:
               cell = cell_dict[cell_name]
               lower_left, upper_right = cell.region.bounding_box
               if np.inf in lower_left or \
                       np.inf in upper_right or \
                       -np.inf in lower_left or \
                       -np.inf in upper_right:
                   xy_center = np.zeros(2)
               else:
                   xy_center = upper_right[0:2] - \
                       (upper_right[0:2] - lower_left[0:2]) / 2

               xy_center_lower_z = np.append(xy_center, lower_left[2])
               translate_args = np.array(lattice_origin + [float(zcoord)]) - \
                   xy_center_lower_z
               # translate the cell
               # may need to rewrite to copy cells
               # if there are multiple of the same
               # universe in a vstack
               cell = translate_obj(cell, translate_args)
               cell_dict[cell_name] = cell
       lattice_universe_name_array = lattice_universe_names

    ## TO IMPLEMENT ##
    # in serpent, hexagonal lattices are rectilinear tilings, wheras
    # in openmc they are concentric hexagonal rings
    #elif re.match("(2|3)", lattice_type):
    #   lattice_pitch = [pitch]
    #   if lattice_type == '2':
    #       orientation = 'y'
    #   else:
    #       orientation = 'x'
    #elif re.match("(2|3|7|8|12|13)"): # hex lattice
    #    lattice_origin = ...
    else:
        raise ValueError(f"Unsupported lattice type: {lattice_type}")

    lattice_origin = tuple(lattice_origin)
    lattice_universe_array = np.empty(lattice_elements, dtype=openmc.Universe)
    for n in np.unique(lattice_universe_name_array):
        lattice_universe_array[np.where(lattice_universe_name_array == n)] = \
            universe_dict[n]

    return lattice_origin, lattice_pitch, lattice_universe_array
