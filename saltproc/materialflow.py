class Materialflow():
    """ Class contains information about material flow and methods how insert
     and extract elements to|from the flow.
    """

    def __init__(
            self,
            mat_name,
            n_iso,
            mass,
            rho,
            mass_flowrate,
            vol_flowrate):
        """ Initializes the class

        Parameters:
        -----------
        mat_name: string
            name of material from SERPENT input file
        n_iso: int
            number of isotopes in the material flow
        mass: 1D ndarray of size n_iso
            mass of isotopes in the material flow (g)
        rho: float
            density of the material flow (g/cm**3)
        mass_flowrate: float
            mass flow rate of the material flow (g/s)
        vol_flowrate: float
            volumetric flow rate of the material flow through reactor (cm**3/s)
        """

    def conservationchecker(self):
        return

    def insert(self):
        return

    def extract(self):
        return
