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

    return [A, B, C, -D]

class NonuniformStackLattice(openmc.Lattice):
    """A lattice consisting of universes stacked nonuniformly along a central
    axis.

    To completley define a nonuniform stack lattice, the
    :attr:`NonuniformStackLattice.central_axis`,
    :attr:`NonuniformStackLattice.pitch`, :attr:`NonuniformStackLattice.outer`,
    and :attr:`NonuniformStackLattice.universes` properties need to be set.

    Most methods for this class use a natural indexing scheme wherein elements
    are assigned an index corresponding to their position relative to the
    :math:`x`, :math:`y`, or :math:`z` bases, depending on the lattice
    orientation, as described fully in :ref:`stack_indexing`, i.e., an index of
    (0) in the lattice oriented to the :math:`z` basis gives the element whose
    `z` coordinate is the smallest. However, note that when universes are
    assigned to lattice elements using the
    :attr:`NonuniformStackLattice.universes` property, the array indices do not
    correspond to natural indices.

    Parameters
    ----------
    lattice_id : int, optional
        Unique identifier for the lattice. If not specified, an identifier will
        automatically be assigned.
    name : str, optional
        Name of the lattice. If not specified, the name is the empty string.

    Attributes
    ----------
    id : int
        Unique identifier for the lattice
    name : str
        Name of the lattice
    pitch : Iterable of float
        Height of the bottom of each lattice cell x, y, or z directions
        (depending on the :attr:`orientation`) in cm.
    outer : openmc.Universe
        A universe to fill all space outside the lattice
    universes : Iterable of openmc.Universe
        A one-dimensional list/array of universes filling each element
        of the lattice. The first dimension corresponds to the
        :attr:`orientation`-direction
    central_axis : Iterable of float
        The :math:`(y,z)`, :math:`(x,z)`, or :math:`(x,y)` coordinates of the central
        axis of the lattice, depending on the lattice orientation
    indices : list of tuple
        A list of all possible lattice element indices. These
        indices correspond to indices in the
        :attr:`NonuniformStackLattice.universes`property.
    levels : int
        An integer representing the number of lattice
        cells along the orientation axis.

    """

    def __init__(self, lattice_id=None, name=''):
        super().__init__(lattice_id, name)

        # Initalize Lattice class attributes
        self._central_axis = None
        self._num_levels = None
        self._orientation = 'z'

    def __repr__(self):
        string = 'StackLattice\n'
        string += '{0: <16}{1}{2}\n'.format('\tID', '=\t', self._id)
        string += '{0: <16}{1}{2}\n'.format('\tName', '=\t', self._name)
        string += '{0: <16}{1}{2}\n'.format('\tOrientation', '=\t',
                                            self._orientation)
        string += '{0: <16}{1}{2}\n'.format('\t# Levels', '=\t', self._num_levels)
        string += '{0: <16}{1}{2}\n'.format('\tcentral_axis', '=\t',
                                            self._central_axis)
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
        return self.universes.shape[0]


    @property
    def central_axis(self):
        return self._central_axis


    @property
    def orientation(self):
        return self._orientation


    @property
    def indices(self):
        if self.ndim == 1:
            return list(np.broadcast(*np.ogrid[:self.num_levels]))
        else:
            raise ValueError("NonuniformStackLattice should only have 1 dimension")


    @property
    def _natural_indices(self):
        """Iterate over all possible lattice element indices.

        """
        if self.ndim == 1:
            n = self.num_levels
            for i in range(n):
                yield i
        else:
            raise ValueError("NonuniformStackLattice should only have 1 dimension")


    @central_axis.setter
    def central_axis(self, central_axis):
        cv.check_type('lattice central_axis', central_axis, Iterable, Real)
        cv.check_length('lattice central_axis', central_axis, 2)
        self._central_axis = central_axis


    @orientation.setter
    def orientation(self, orientation):
        cv.check_value('orientation', orientation.lower(), ('x','y','z'))
        self._oreientation = orientation.lower()


    @openmc.Lattice.pitch.setter
    def pitch(self, pitch):
        cv.check_type('lattice pitch', pitch, Iterable, Real)
        cv.check_length('lattice pitch', pitch, self.num_levels)
        self._pitch = pitch


    @openmc.Lattice.universes.setter
    def universes(self, universes):
        cv.check_iterable_type('lattice universes', universes, openmc.UniverseBase, min_depth=1, max_depth=1)
        self._universes = np.asarray(universes)


    def find_element(self, point):
        """Determine index of lattice element and local coordinates for a point

        Parameters
        ----------
        point : Iterable of float
            Cartesian coordinates of point

        Returns
        -------
        int
            The corresponding lattice element index
        3-tuple of float
            Carestian coordinates of the point in the corresponding lattice
            element coordinate system

        """
        if self.oriention == 'x':
            _idx = 0
        elif self.orientation == 'y':
            _idx = 1
        else:
            _idx = 2

        # find the level:
        p = point(_idx)
        idx = 0
        while not(p >= self.pitch[idx] and p <= self.pitch[idx + 1]):
               idx += 1

        return idx, self.get_local_coordinates(point, idx)


    def get_local_coordinates(self, point, idx):
        """Determine local coordinates of a point within a lattice element

        Parameters
        ----------
        point : Iterable of float
            Cartesian coordinates of point
        idx : int
            index of lattice element

        Returns
        -------
        3-tuple of float
            Cartesian coordinates of point in the lattice element coordinate
            system
        """
        x,y,z = point
        c1, c2 = self.central_axis
        if self.oriention == 'x':
            x -= self.pitch[idx]
            y -= c1
            z -= c2
        elif self.orientation == 'y':
            x -= c1
            y -= self.pitch[idx]
            z -= c2
        else:
            x -= c1
            y -= c2
            z -= self.pitch[idx]

        return (x,y,z)


    def get_universe_index(self, idx):
        """Return index in the universes array corresponding
        to a lattice element index

        Parameters
        ----------
        idx : int
            Lattice element index

        Returns
        -------
        int
            Index used when setting the :attr:`NonuniformStackLattice.universes` property

        """
        return idx


    def is_valid_index(self, idx):
        """Determine whether lattice element index is within defined range

        Parameters
        ----------
        idx : int
            Lattice element index

        Returns
        -------
        bool
            Whether index is valid

        """
        if self.ndim == 1:
            return (0 <= idx < self.num_levels)
        else:
            raise ValueError("StackLattice must have only one dimension")

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
        if memo and self in memo:
            return
        if memo is not None:
            memo.add(self)

        lattice_subelement = ET.Element("lattice")
        lattice_subelement.set("id", str(self._id))
        if len(self._name) > 0:
            lattice_subelement.set("name", str(self._id))

        # Export the Lattice cell pitch
        pitch = ET.SubElement(lattice_subelement, "pitch")
        pitch.text = ' '.join(map(str, self._pitch))

        # Export the Lattice outer Universe (if specified)
        if self._outer is not None:
            outer = ET.SubElement(lattice_subelement, "outer")
            outer.text = str(self._outer._id)
            self._outer.create_xml_subelement(xml_element, memo)

        # Export Lattice cell levels
        levels = ET.SubElement(lattice_subelement, "levels")
        levels.text = ' '.join(map(str, self.num_levels))

        # Export lattice orientation
        lattice_subelement.set("orientation", self._orientation)

        # Export Lattice central axis
        central_axis = ET.SubElement(lattice_subelement, "central_axis")
        central_axis.text = ' '.join(map(str, self._central_axis))

        # Export the Lattice nested Universe IDs - column major for Fortran
        universe_ids = '\n'

        # 1D stack
        if self.ndim == 1:
            for l in range(self.num_levels):
                universe = self._universes[l]
                # Append Universe ID to the Lattice XML subelement
                universe_ids += f'{universe._id} '

                # Create XML subelement for this Universe
                universe.create_xml_subelement(xml_element, memo)

                # Add newline for each level
                universe_ids += '\n'

        # Remove trailing newline character from Universe IDs string
        universe_ids = universe_ids.rstrip('\n')

        universes = ET.SubElement(lattice_subelement, "universes")
        universes.text = universe_ids

        # Append the XML subelement for this Lattice to the XML element
        xml_element.append(lattice_subelement)


    @classmethod
    def from_xml_element(cls, elem, get_universe):
        """Generate nonuniform stack lattice from XML element

        Parameters
        ----------
        elem : xml.etree.ElementTree.Element
            `<lattice>` element
        get_universe : function
            Function returning universe (defined in
            :meth:`openmc.Geometry.from_xml`)

        Returns
        -------
        NonuniformStackLattice
            Nonuniform stack lattice

        """
        lat_id = int(get_text(elem, 'id'))
        name = get_text(elem, 'name')
        lat = cls(lat_id, name)
        lat.central_axis = [float(i)
                          for i in get_text(elem, 'central_axis').split()]
        lat.pitch = [float(i) for i in get_text(elem, 'pitch').split()]
        outer = get_text(elem, 'outer')
        if outer is not None:
            lat.outer = get_universe(int(outer))

        # Get array of universes
        levels = get_text(elem, 'levels').split()
        shape = np.array(levels, dtype=int)[::-1]
        uarray = np.array([get_universe(int(i)) for i in
                           get_text(elem, 'universes').split()])
        uarray.shape = shape
        lat.universes = uarray
        return lat

    @classmethod
    def from_hdf5(cls, group, universes):
        """Create nonuniform stack lattice from HDF5 group

        Parameters
        ----------
        group : h5py.Group
            Group in HDF5 file
        universes : dict
            Dictionary mapping universe IDs to instances of
            :class:`openmc.Universe`.

        Returns
        -------
        openmc.NonuniformStackLattice
            Nonuniform stack lattice

        """

        levels = group['levels'][...]
        central_axis = group['central_axis'][...]
        pitch = group['pitch'][...]
        outer = group['outer'][()]
        universe_ids = group['universes'][...]

        # Create the Lattice
        lattice_id = int(group.name.split('/')[-1].lstrip('lattice '))
        name = group['name'][()].decode() if 'name' in group else ''
        lattice = cls(lattice_id, name)
        lattice.central_axis = central_axis
        lattice.pitch = pitch

        # If the Universe specified outer the Lattice is not void
        if outer >= 0:
            lattice.outer = universes[outer]

        # Build array of Universe pointers for the Lattice
        uarray = np.empty(universe_ids.shape, dtype=openmc.Universe)

        for l in range(universe_ids.shape[0]):
            uarray[l] = universes[universe_ids[l]]

        # Set the universes for the lattice
        lattice.universes = uarray

        return lattice


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
        (y,z), (x,z), or (x,y).
    r1 : float
        Half-width of octagon across axis-perpendicualr sides
    r2 : float
        Half-width of octagon across off-axis sides
    axis : char
        Central axis of ocatgon. Defaults to 'z'

    Attributes
    ----------
    top : openmc.ZPlane or openmc.XPlane
        Top planar surface of octagon
    bottom : openmc.ZPlane or openmc.XPlane
        Bottom planar surface of octagon
    right: openmc.YPlane or openmc.ZPlane
        Right planaer surface of octagon
    left: openmc.YPlane or openmc.ZPlane
        Left planar surface of octagon
    upper_right : openmc.Plane
        Upper right planar surface of octagon
    lower_right : openmc.Plane
        Lower right planar surface of octagon
    lower_left : openmc.Plane
        Lower left planar surface of octagon
    upper_left : openmc.Plane
        Upper left planar surface of octagon

    """

    _surface_names = ('top', 'bottom',
                      'upper_right', 'lower_left',
                      'right', 'left',
                      'lower_right', 'upper_left')

    def __init__(self, center, r1, r2, axis='z', **kwargs):
        self._axis = axis
        q1c, q2c = center

        # Coords for axis-perpendicular planes
        ctop = q1c+r1
        cbottom = q1c-r1

        cright= q2c+r1
        cleft = q2c-r1

        # Side lengths
        L_perp_ax1 = (r2 * np.sqrt(2) - r1) * 2
        L_perp_ax2 = (r1 * np.sqrt(2) - r2) * 2

        # Coords for quadrant planes
        p1_upper_right = [L_perp_ax1/2, r1, 0]
        p2_upper_right = [r1, L_perp_ax1/2, 0]
        p3_upper_right = [r1, L_perp_ax1/2, 1]

        p1_lower_right = [r1, -L_perp_ax1/2, 0]
        p2_lower_right = [L_perp_ax1/2, -r1, 0]
        p3_lower_right = [L_perp_ax1/2, -r1, 1]

        points = [p1_upper_right, p2_upper_right, p3_upper_right,
                  p1_lower_right, p2_lower_right, p3_lower_right]

        # Orientation specific variables
        if axis == 'x':
            coord_map = [2,0,1]
            self.top = openmc.ZPlane(z0=ctop, **kwargs)
            self.bottom = openmc.ZPlane(z0=cbottom, **kwargs)
            self.right = openmc.YPlane(y0=cright, **kwargs)
            self.left = openmc.YPlane(y0=cleft, **kwargs)

        elif axis == 'y':
            coord_map = [0,2,1]
            self.top = openmc.ZPlane(z0=ctop, **kwargs)
            self.bottom = openmc.ZPlane(z0=cbottom, **kwargs)
            self.right = openmc.XPlane(x0=cright, **kwargs)
            self.left = openmc.XPlane(x0=cleft, **kwargs)

        elif axis == 'z':
            coord_map = [0,1,2]
            self.top = openmc.YPlane(y0=ctop, **kwargs)
            self.bottom = openmc.YPlane(y0=cbottom, **kwargs)
            self.right = openmc.XPlane(x0=cright, **kwargs)
            self.left = openmc.XPlane(x0=cleft, **kwargs)


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

        self.upper_right = openmc.Plane(*tuple(upper_right_params), **kwargs)
        self.lower_right = openmc.Plane(*tuple(lower_right_params), **kwargs)
        self.lower_left = openmc.Plane(*tuple(lower_left_params), **kwargs)
        self.upper_left = openmc.Plane(*tuple(upper_left_params), **kwargs)


    def __neg__(self):
        reg = -self.top & +self.bottom & -self.right & +self.left
        if self._axis == 'y':
            reg = reg & -self.upper_right & -self.lower_right & \
                +self.lower_left & +self.upper_left
        else:
            reg = reg & +self.upper_right & +self.lower_right & \
                -self.lower_left & -self.upper_left

        return reg


    def __pos__(self):
        reg = +self.top | -self.bottom | +self.right | -self.left
        if self._axis == 'y':
            reg = reg | +self.upper_right | +self.lower_right | \
                -self.lower_left | -self.upper_left
        else:
            reg = reg | -self.upper_right | -self.lower_right | \
                +self.lower_left | +self.upper_left

        return reg



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
        Angular segmentation in degrees relative to the x-axis

    Attributes
    ----------
    outer : openmc.ZCylinder
        Outer cylinder surface
    inner : openmc.ZCylinder
        Inner cylinder surface
    plane_1 : openmc.Plane
        Segment plane corresponding to :attr:`alpha1`
    plane_2 : openmc.Plane
        Segmenting plane correspodning to :attr:`alpha2`

    """

    _surface_names = ('outer','inner',
                      'plane_a', 'plane_b')

    def __init__(self, center, r1, r2, alpha1, alpha2, **kwargs):

        alpha1 = np.pi / 180 * alpha1
        alpha2 = np.pi / 180 * alpha2
        xc,yc = center
        # Coords for axis-perpendicular planes
        p1 = np.array([0,0,1])

        p2_plane1 = np.array([r1 * np.cos(alpha1), -r1 * np.sin(alpha1), 0])
        p3_plane1 = np.array([r2 * np.cos(alpha1), -r2 * np.sin(alpha1), 0])

        p2_plane2 = np.array([r1 * np.cos(alpha2), r1 * np.sin(alpha2), 0])
        p3_plane2 = np.array([r2 * np.cos(alpha2), r2 * np.sin(alpha2), 0])

        plane1_params = _plane_from_points(p1, p2_plane1, p3_plane1)
        plane2_params = _plane_from_points(p1, p2_plane2, p3_plane2)

        self.inner = openmc.ZCylinder(x0=xc, y0=yc, r=r1, **kwargs)
        self.outer = openmc.ZCylinder(x0=xc, y0=yc, r=r2, **kwargs)
        self.plane1 = openmc.Plane(*plane1_params, **kwargs)
        self.plane2 = openmc.Plane(*plane2_params, **kwargs)


    def __neg__(self):
        return -self.outer & +self.inner & -self.plane1 &  +self.plane2


    def __pos__(self):
        return +self.outer | -self.inner | +self.plane1 | -self.plane2


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
        theta = np.arctan(r/h)
        r2 = (1 / np.cos(theta))**2 - 1

        self.cone = openmc.model.ZConeOneSided(x0=xb,y0=yb,z0=h+zb,r2=r2,up=False, **kwargs)
        self.bottom = openmc.ZPlane(z0=zb)


    def __neg__(self):
        return -self.cone & +self.bottom


    def __pos__(self):
        return +self.cone | -self.bottom
