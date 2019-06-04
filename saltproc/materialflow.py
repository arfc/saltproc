from pyne.material import Material as pymat
import copy
import sys
from collections import Counter


class Materialflow(pymat):
    """ Class contains information about material flow and methods how insert
     and extract elements to|from the flow.
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
        """Initializes the class

        Parameters:
        -----------
        PyNE.Material: class
            PyNE Material parent class containing nuclide vector, density,
            mass, atoms_per_molecule, metadata
        temp: float
            temperature of the material flow (K)
        mass_flowrate: float
            mass flow rate of the material flow (g/s)
        void_frac: float
            void fraction in the material (%)
        burnup: float
            material burnup at the end of depletion step [MWd/kgU]
        """
        # initialize parent class attributes
        super().__init__()
        # initialize all object attributes
        self.vol = vol
        self.temp = temp
        self.mass_flowrate = mass_flowrate
        self.void_frac = void_frac
        self.burnup = burnup

    def conservationchecker(self):
        return

    def get_mass(self):
        return self.mass

    def print_attr(self):
        print("Volume %f cm3" % self.vol)
        print("Mass %f g" % self.mass)
        print("Density %f g/cm3" % self.density)
        print("Atoms per molecule %f " % self.atoms_per_molecule)
        print("Meta %s " % self.metadata)
        print("Mass flowrate %f g/s" % self.mass_flowrate)
        print("Temperature %f K" % self.temp)
        print("Void fraction %f " % self.void_frac)
        print("Burnup %f MWd/kgU" % self.burnup)
        print("U-235 mass %f g" % self[922350000])
        print("Li-7 mass %f g" % self[30070000])

    def scale_matflow(self, f=1.0):
        """ Returns nuclide vector dictionary, obtained from self and scaled by
         f
        """
        old_dict = dict(self.comp)
        old_nucvec = {}
        for key, value in old_dict.items():
            old_nucvec[key] = f * self.mass * value
        return old_nucvec

    def copy_pymat_attrs(self, src):
        """ Modifies Materialflow object by copying PyNE attributites from src
        """
        setattr(self, 'density', copy.deepcopy(src.density))
        setattr(self,
                'atoms_per_molecule',
                copy.deepcopy(src.atoms_per_molecule))
        self.metadata = src.metadata

    def copy_and_scale(self, f):
        """ Returns new copied Materialflow based on self, with composition
         and mass flowrate scale by factor of f
        """
        # Initiate new object my copying class from self
        outflow = copy.deepcopy(self)
        # print ("Scale outflow ", outflow.__class__)
        # Scale Materialflow an renormilize
        outflow.mass = f * self.mass
        outflow.norm_comp()
        # Scale mass flowrate and volume too
        setattr(outflow, 'mass_flowrate', copy.deepcopy(f*self.mass_flowrate))
        setattr(outflow, 'vol', copy.deepcopy(f*self.vol))
        # print("Mass ", outflow.mass, self.mass)
        # print("Flow ", outflow.mass_flowrate, self.mass_flowrate)
        # print("Vol ", outflow.vol, self.vol)
        # print("Density ", outflow.density, self.density)
        # print("Atoms ", outflow.atoms_per_molecule, self.atoms_per_molecule)
        return outflow

    def __deepcopy__(self, memo):
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
        if not isinstance(other, Materialflow):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.mass == other.mass and self.vol == other.vol \
            and self.density == other.density \
            and self.atoms_per_molecule == other.atoms_per_molecule \
            and self.temp == other.temp \
            and self.mass_flowrate == other.mass_flowrate \
            and self[922350000] == other[922350000] \
            and self[922380000] == other[922380000] \
            and self[721780001] == other[721780001]
    #
    # Materialflow operation Overloads
    #

    def __add__(x, y):
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
        result.burnup = (x.burnup*x.mass + y.burnup*y.mass)/result.mass
        # result.density = result.mass/result.vol
        result.density = x.density
        result.vol = result.mass/result.density
        result.void_frac = (x.void_frac*x.vol + y.void_frac*y.vol)/result.vol
        return result

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            result = copy.deepcopy(self)
            result.mass = other * self.mass
            result.norm_comp()
            result.vol = other * self.vol
            result.mass_flowrate = other * self.mass_flowrate
            # result.temp = (x.temp*x.mass + y.temp*y.mass)/result.mass
            return result
        else:
            NotImplemented

"""
fuel = Materialflow({922350: 0.04, 922380: 0.96},
                    122000000,
                    4.9602,
                    temp=923,
                    mass_flowrate=0.5e+6,
                    void_frac=1.0)

print(fuel)
print(fuel.comp)
print(fuel.mass)
print(fuel.density)
print(fuel.atoms_per_molecule)
print(fuel.metadata)

print('Fuel salt temperature %f K' % fuel.temp)
print('Mass flowrate %f g/s' % fuel.mass_flowrate)
print('Void fraction %f %%' % fuel.void_frac)
print('Mass %f g' % fuel.get_mass())"""
