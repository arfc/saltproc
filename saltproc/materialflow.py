"""Materialflow module"""
import copy
import math
from collections import Counter

import numpy as np

from openmc import Material

class Materialflow(Material):
    """ Class contains information about burnable material flow. Child class of
    :class:`openmc.Material`.

    Parameters
    ----------
    comp : dict of str to float
        Dictionary mapping element or nuclide names to their weight
        percent.
    density : float
        Material density [g/cm^3]
    volume : float
        Material volume [cm^3]
    mass_flowrate : float
        mass flow rate of the material flow [g/s]
    void_frac : float
        void fraction in the material [%]
    burnup : float
        material burnup at the end of depletion step [MWd/kgU]
    kwargs : dict
        Key-word arguemnts for :class:`openmc.Material`

    """

    def __init__(
            self,
            comp=None,
            comp_is_density=False,
            density=None,
            volume=1.0,
            mass_flowrate=0.0,
            void_frac=0.0,
            burnup=0.0,
            **kwargs):
        """ Initializes the Materialflow object.

        """
        # initialize parent class attributes
        super().__init__(**kwargs)

        # initialize all object attributes
        if volume is not None:
            self.volume = volume
        if density is not None:
            self.set_density('g/cm3', density)
        self.mass_flowrate = mass_flowrate
        self.void_frac = void_frac
        self.burnup = burnup

        if bool(comp):
            self.replace_components(comp, comp_is_density)
        else:
            self.mass = 0.0

    def replace_components(self, comp, comp_is_density=False):
        """Replace and normalize the material composition

        Parameters
        ----------
        comp : dict of str to float
            Dictionary mapping element or nuclide names to their atom or weight
            percent.
        percent_type : {'wo', 'ao'}
            'ao' for atom percenta nd 'wo' for weight percent.

        """
        for nuclide in self.get_nuclides():
            self.remove_nuclide(nuclide)

        nucs = np.array(list(comp.keys()))
        nonzeros = np.array(list(comp.values()))
        if len(nucs) > 0:
            comp = dict(zip(nucs, nonzeros))
            super().add_components(comp, percent_type='wo')
            density = self.get_density()
            # mass dens to wt-%
            if comp_is_density:
                for nuc in nucs:
                    super().remove_nuclide(nuc)
                    comp[nuc] = comp[nuc] / density
                    super().add_nuclide(nuc, comp[nuc], percent_type='wo')
                self.set_density('g/cm3', density)
            self.mass = density * self.volume
            self.comp = comp
        else:
            self.comp = comp
            self.mass = 0.0

    def get_mass(self, nuc=None, openmc=False):
        if not openmc:
            if bool(nuc):
                mass = self.comp[nuc] * self.mass
            else:
                mass = self.mass
        else:
            mass = super().get_mass(nuc)
        return mass

    def get_density(self):
        if self.density_units != 'g/cm3':
            density = self.get_mass_density()
        else:
            density = self.density
        return density

    def print_attr(self):
        """Prints various attributes of Materialflow object.
        """
        print("Volume %f cm3" % self.volume)
        print("Mass %f g" % self.mass)
        print("Density %f g/cm3" % self.density)
        print("Mass flowrate %f g/s" % self.mass_flowrate)
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
            Nuclide component dictionary of relative mass.

            ``key``
                The keys are preserved from PyNE Material (integers
                representing nuclides in id-form).
            ``value``
                factor f.

        """
        new_mat_comp = {}
        for key, value in self.comp.items():
            new_mat_comp[key] = f * self.mass * value
        return new_mat_comp

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
        cls = self.__class__
        result = cls(comp=self.comp.copy(),
                     density=self.mass / self.volume,
                     volume=self.volume,
                     mass_flowrate=self.mass_flowrate,
                     void_frac=self.void_frac,
                     burnup=self.burnup)
        return result

    def __eq__(self, other):
        """Overrides Python ``=`` operation to compare two Materialflow
        objects. Compares objects total mass, volume,
        and mass flowrate.

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

        value = math.isclose(self.mass,
                             other.mass,
                             abs_tol=1e-15) \
            and self.volume == other.volume \
            and self.mass_flowrate == other.mass_flowrate

        return value

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
        if (x.mass == 0.0 or x.volume == 0.0) \
                and (y.mass != 0.0 and y.volume != 0.0):
            return y
        elif (x.mass != 0.0 and x.volume != 0.0) \
                and (y.mass == 0.0 or y.volume == 0.0):
            return x
        else:
            cls = x.__class__
            result = cls.__new__(cls)

            result_mass = x.mass + y.mass

            x_density = x.mass / x.volume
            y_density = y.mass / y.volume

            result_density = x_density

            result_volume = result_mass / result_density
            result = Materialflow(density=result_density, volume=result_volume)

            def get_mass_dict(matflow):
                nuclides = list(matflow.comp.keys())
                masses = matflow.get_mass() * np.array(list(matflow.comp.values()))
                return dict(zip(nuclides, masses))

            x_mass_dict = Counter(get_mass_dict(x))
            y_mass_dict = Counter(get_mass_dict(y))
            x_mass_dict.update(y_mass_dict)
            x_mass_dict = dict(x_mass_dict)
            masses = np.array(list(x_mass_dict.values())) / result_mass
            result_comp = dict(zip(x_mass_dict.keys(), masses))
            result.replace_components(result_comp)
            result.mass_flowrate = x.mass_flowrate + y.mass_flowrate
            # Burnup is simply averaged by should be renormalized by heavy metal
            # use self.fissionable_mass?
            result.burnup = (x.burnup * x.mass + y.burnup * y.mass) / result_mass
            result.void_frac = (
                x.void_frac * x.volume + y.void_frac * y.volume) / result.volume
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
            if scaling_factor != 1.0 or scaling_factor != 1:
                result.volume = scaling_factor * self.volume
                result.mass = result.volume * result.get_density()
                result.mass_flowrate = scaling_factor * self.mass_flowrate
            return result
        else:
            NotImplemented
