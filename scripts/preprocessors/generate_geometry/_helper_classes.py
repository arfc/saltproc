import numpy as np
import openmc
import openmc.model

def _plane_from_points(p1, p2, p3):
    # get plane from points p1, p2, p3
    n = np.cross(p2 - p1, p3 - p1)
    n0 = -p1
    A = n[0]
    B = n[1]
    C = n[2]
    D = np.dot(n, n0)

    return [A, B, C, D]

class StackLattice(openmc.Lattice):
    """1D stack lattice
    """

    def __init__(self, lattice_id=None, name=''):
        super().__init__(lattice_id, name)

        # Initalize Lattice class attributes
        self._center = None
        self._num_levels = None
        self._orientation = 'z'

    def __repr__(self):
        string = 'StackLattice\n'
        string += '{0: <16}{1}{2}\n'.format('\tID', '=\t', self._id)
        string += '{0: <16}{1}{2}\n'.format('\tName', '=\t', self._name)
        string += '{0: <16}{1}{2}\n'.format('\tOrientation', '=\t',
                                            self._orientation)
        string += '{0: <16}{1}{2}\n'.format('\t# Levels', '=\t', self._num_levels)
        string += '{0: <16}{1}{2}\n'.format('\tCenter', '=\t',
                                            self._center)
        string += '{0: <16}{1}{2}\n'.format('\tPitch', '=\t', self._pitch)
        if self._outer is not None:
            string += '{0: <16}{1}{2}\n'.format('\tOuter', '=\t',
                                                self._outer._id)
        else:
            string += '{0: <16}{1}{2}\n'.format('\tOuter', '=\t',
                                                self._outer)

        string += '{: <16}\n'.format('\tUniverses')

        for i, universe in enumerate(np.ravel(self._universes)):
            string += f'universe._id\n'

        string = string.rstrip('\n')

        return string

    @property
    def num_levels(self):
        return self._num_levels

    @property
    def center(self):
        return self._center

    @property
    def orientation(self):
        return self._orientation

    @property
    def indices(self):
        ...

    @property
    def _natural_inidices(self):
        ...

    @num_levels.setter
    def num_levels(self,...):
        ...

    @center.settter
    def center(self,...):
        ...

    @orientation.setter(self,...):
        ...

    @Lattice.pitch.setter(self,...):
        ...

    @Lattice.universes.setter(self,...):
        ...

    def find_element(self, point):
        """Determine index of lattice element and local coordinates for a point

        Parameters
        ----------
        point : Iterable of float
            Cartesian coordinates of point

        Returns
        -------
        2- or 3-tuple of int
            A tuple of the corresponding (x,y,z) lattice element indices
        3-tuple of float
            Carestian coordinates of the point in the corresponding lattice
            element coordinate system

        """
        ...

    def get_local_coordinates(self, point, idx):
        """Determine local coordinates of a point within a lattice element

        Parameters
        ----------
        point : Iterable of float
            Cartesian coordinates of point
        idx : Iterable of int
            (x,y,z) indices of lattice element. If the lattice is 2D, the z
            index can be omitted.

        Returns
        -------
        3-tuple of float
            Cartesian coordinates of point in the lattice element coordinate
            system
        """
        ...


    def get_universe_index(self, idx):
        """Return index in the universes array corresponding
        to a lattice element index

        Parameters
        ----------
        idx : Iterable of int
            Lattice element indices in the :math:`(x,y,z)` coordinate system

        Returns
        -------
        2- or 3-tuple of int
            Indices used when setting the :attr:`RectLattice.universes` property

        """
        ...


    def is_valid_index(self, idx):
        """Determine whether lattice element index is within defined range

        Parameters
        ----------
        idx : Iterable of int
            Lattice element indices in the :math:`(x,y,z)` coordinate system

        Returns
        -------
        bool
            Whether index is valid

        """
        ...

    def create_xml_subelement(self, xml_element, memo=None):
        """Add the lattice xml representation to an incoming xml element

        Parameters
        ----------
        xml_element : xml.etree.ElementTree.Element
            XML element to be added to

        memo : set or None
            A set of object id's representing geometry entities already
            written to the xml_element. This parameter is used internally
            and should not be specified by users.

        Returns
        -------
        None

        """
        ...

    @classmethod
    def from_xml_element(cls, elem, get_universe):
        """Generate rectangular lattice from XML element

        Parameters
        ----------
        elem : xml.etree.ElementTree.Element
            `<lattice>` element
        get_universe : function
            Function returning universe (defined in
            :meth:`openmc.Geometry.from_xml`)

        Returns
        -------
        StackLattice
            Stack lattice

        """
        ...

    @classmethod
    def from_hdf5(cls, group, universes):
        """Create rectangular lattice from HDF5 group

        Parameters
        ----------
        group : h5py.Group
            Group in HDF5 file
        universes : dict
            Dictionary mapping universe IDs to instances of
            :class:`openmc.Universe`.

        Returns
        -------
        openmc.StackLattice
            Stack lattice

        """
        ...
    # junk from _script helpers
        # rest of this will get deleted later
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


class FiniteCone(openmc.model.CompositeSurface):
    """Finite cone composite surface. Parallel to z-axis

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
    cone : openmc.model.ZConeOneSided
        Outer cylinder surface
    bottom : openmc.ZPlane

    """

    _surface_names = ('cone', 'bottom')

    def __init__(self, base, r, h, **kwargs):

        xb,yb,zb = base

        self.cone = openmc.model.ZConeOneSided(x0=xb,y0=yb,z0=h-zb,r2=r,up=False)
        self.bottom = openmc.ZPlane(z0=zb)


    def __neg__(self):
        return -self.cone & +self.bottom


    def __pos__(self):
        return +self.cone | -self.bottom
