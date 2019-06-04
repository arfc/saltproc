from pyne.material import Material as pymat
import copy
import sys


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
            mass_flowrate=1.0,
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

    def __deepcopy__(self, memo):
        # Initiate new object my copying class from self
        cls = self.__class__
        result = cls.__new__(cls)
        # Copy nuclide vector from self
        old_dict = dict(self.comp)
        old_nucvec = {}
        for key, value in old_dict.items():
            old_nucvec[key] = self.mass * value
        # Use nuclide vector to define Materialflow object
        result = Materialflow(old_nucvec)
        # Copy Materialflow density and atoms_per_molecule
        setattr(result, 'density', copy.deepcopy(self.density))
        setattr(result,
                'atoms_per_molecule',
                copy.deepcopy(self.atoms_per_molecule))
        # Copy other object attributes such as volume, burnup, etc
        for k, v in self.__dict__.items():
            if 'comp' not in k:
                setattr(result, k, copy.deepcopy(v))
        print(self.density, result.density)
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
