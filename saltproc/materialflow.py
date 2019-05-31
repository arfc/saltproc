from pyne.material import Material as pymat


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
