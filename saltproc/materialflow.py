from pyne.material import Material as pymat
import copy
from collections import Counter


class Materialflow(pymat):
    """ Class contains information about burnable material flow. Based on :class:`pyne.Material`.
    """

    def __init__(
            self,
            comp=None,
            mass=-1.0,
            density=1.0,
            atoms_per_molecule=-1.0,
            metadata=None,
            vol=1.0,
            temp=900,
            mass_flowrate=0.0,
            void_frac=0.0,
            burnup=0.0):
        """ Initializes the Materialflow object.

        Parameters
        ----------

        :class:`pyne.Material`
            PyNE Material parent class containing nuclide vector, density,
            mass, atoms_per_molecule, metadata
        temp : float
            temperature of the material flow (K)
        mass_flowrate : float
            mass flow rate of the material flow (g/s)
        void_frac : float
            void fraction in the material (%)
        burnup : float
            material burnup at the end of depletion step [MWd/kgU]
        """
        # initialize parent class attributes
        # super().__init__()
        # initialize all object attributes
        self.vol = vol
        self.temp = temp
        self.mass_flowrate = mass_flowrate
        self.void_frac = void_frac
        self.burnup = burnup

    def get_mass(self):
        """Returns total mass of the material descibed in Materialflow object.

        Returns
        -------
        float
            The mass of the object.

        """
        return self.mass

    def print_attr(self):
        """Prints various attributes of Materialflow object.
        """
        print("Volume %f cm3" % self.vol)
        print("Mass %f g" % self.mass)
        print("Density %f g/cm3" % self.density)
        print("Atoms per molecule %f " % self.atoms_per_molecule)
        print("Meta %s " % self.metadata)
        print("Mass flowrate %f g/s" % self.mass_flowrate)
        print("Temperature %f K" % self.temp)
        print("Void fraction %f " % self.void_frac)
        print("Burnup %f MWd/kgU" % self.burnup)

    def scale_matflow(self, f=1.0):
        """Returns nuclide vector dictionary, obtained from object attrs and
        then scaled by factor.

        Parameters
        ----------
        f : float
            Scaling factor.

        Returns
        -------
        new_mat_comp : dict of int to float
            Materialflow nuclide component dictionary of relative mass.

            ``key``
                The keys are preserved from PyNE Material (integers
                representing nuclides in id-form).
            ``value``
                Each nuclide's mass fraction, multiplied by
                factor f.

        """
        old_dict = dict(self.comp)
        new_mat_comp = {}
        for key, value in old_dict.items():
            new_mat_comp[key] = f * self.mass * value
        return new_mat_comp

    def copy_pymat_attrs(self, src):
        """Copies PyNE attributites from source object (`src`) to target
        object.

        Parameters
        ----------
        src : obj
            Materialflow object to copy attributes from.

        """
        setattr(self, 'density', copy.deepcopy(src.density))
        setattr(self,
                'atoms_per_molecule',
                copy.deepcopy(src.atoms_per_molecule))
        self.metadata = src.metadata

    def __deepcopy__(self, memo):
        """Return a deep copy of compound object `self`.

        Parameters
        ----------
        self : obj
            Compound object.
        memo : dict, optional
            Id-to-object correspondence to control for recursion.

        Returns
        -------
        obj
            New compound object copied from `self`.

        """
        # Initiate new object my copying class from self
        cls = self.__class__
        result = cls.__new__(cls)
        # Copy nuclide vector from self
        result = Materialflow(self.scale_matflow())
        # Copy Materialflow density and atoms_per_molecule
        result.copy_pymat_attrs(self)
        # Copy other object attributes such as volume, burnup, etc
        for k, v in self.__dict__.items():
            if 'comp' not in k:
                setattr(result, k, copy.deepcopy(v))
        return result

    def __eq__(self, other):
        """Overrides Python ``=`` operation to compare two Materialflow
        objects. Compares objects total mass, density, atoms_per_molecule,
        temperature, mass flowrate, and masses of important isotopes:
        uranium-235 and uranium-238.

        Parameters
        ----------
        other : obj
            Materialflow object to compare with.

        Returns
        -------
        bool
            Are the objects equal?

        """
        if not isinstance(other, Materialflow):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.mass == other.mass and self.vol == other.vol \
            and self.density == other.density \
            and self.atoms_per_molecule == other.atoms_per_molecule \
            and self.temp == other.temp \
            and self.mass_flowrate == other.mass_flowrate \
            and self[922350000] == other[922350000] \
            and self[922380000] == other[922380000]
    #
    # Materialflow math operation Overloads
    #

    def __add__(x, y):
        """Overrides Python adding operation for Materialflow objects.

        Parameters
        ----------
        x : obj
            Materialflow object #1.
        y : obj
            Materialflow object #2.

        Returns
        -------
        obj
            Materialflow which is a sum of isotope masses from `x` and `y`.

        """
        cls = x.__class__
        result = cls.__new__(cls)
        result.mass = x.mass + y.mass
        x_comp = Counter(x)
        y_comp = Counter(y)
        x_comp.update(y_comp)
        result.comp = dict(x_comp)
        result.norm_comp()
        result.mass_flowrate = x.mass_flowrate + y.mass_flowrate
        # result.temp = (x.temp*x.mass + y.temp*y.mass)/result.mass  # averaged
        result.temp = x.temp
        # Burnup is simply averaged by should be renormilized by heavy metal
        result.burnup = (x.burnup * x.mass + y.burnup * y.mass) / result.mass
        # result.density = result.mass/result.vol
        result.density = x.density
        result.vol = result.mass / result.density
        result.void_frac = (
            x.void_frac * x.vol + y.void_frac * y.vol) / result.vol
        return result

    def __rmul__(self, scaling_factor):
        """Overrides Python multiplication operation for Materialflow objects.

        Parameters
        ----------
        scaling_factor : float or int
            Scaling factor.

        Returns
        -------
        obj
            Materialflow object which has mass of each isotope and
            mass_flowrate scaled by `other`.

        """
        if isinstance(scaling_factor, (int, float)):
            result = copy.deepcopy(self)
            result.mass = scaling_factor * self.mass
            result.norm_comp()
            result.vol = scaling_factor * self.vol
            result.mass_flowrate = scaling_factor * self.mass_flowrate
            # result.temp = (x.temp*x.mass + y.temp*y.mass)/result.mass
            return result
        else:
            NotImplemented
