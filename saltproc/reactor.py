class Reactor ():
    """ Class contains information about current state of the reactor.
    """

    def __init__(
            self,
            volume,
            mass_flowrate,
            power_levels,
            depl_hist):
        """ Initializes the class
        Parameters:
        -----------
        volume: float
            total volume of reactor core (cm**3)
        mass_flowrate: float
            total mass flowrate through reactor (g/s)
        power_levels: array [Tx1]
            normalized power level in Watts for each depletion step
        dep_hist: array [Tx1]
            metric tons of heavy metals for the end of each time step (MTHM)
        """
        # initialize all object attributes
        self.volume = volume
        self.mass_flowrate = mass_flowrate
        self.power_levels = power_levels
        self.depl_hist = depl_hist
