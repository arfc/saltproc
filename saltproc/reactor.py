class Reactor ():
    """ Class contains information about current state of the reactor.
    """

    def __init__(
            self,
            name,
            volume,
            mass_flowrate,
            power_level,
            fp_powdens,
            composition,
            mthm):
        """ Initializes the class
        Parameters:
        -----------
        name: string
            name of the reactor design
        volume: float
            total volume of reactor core (cm**3)
        mass_flowrate: float
            total mass flowrate through reactor (g/s)
        power_level: array [Tx1]
            normalized power level in percents (%) for each depletion step
        fp_powdens: float
            full power density (kW/g) in depletion simulation
        composition: array [iso x T x number of depleted materials]
            mass of each isotope for the end of each timestep for every fluid
            (g)
        mthm: array [Tx1]
            metric tons of heavy metals for the end of each time step (MTHM)
        """
        # initialize all object attributes
        self.name = name
        self.volume = volume
        self.mass_flowrate = mass_flowrate
        self.power_level = power_level
        self.fp_powdens = fp_powdens
