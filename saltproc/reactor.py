class Reactor ():
    """
    Class contains information about current state of the reactor.
    """

    def __init__(
            self,
            volume,
            mass_flowrate,
            power_levels,
            depl_hist):
        """Initializes the class.

        Parameters
        ----------
        volume : float
            Total volume of the reactor core (:math:`cm^3`).
        mass_flowrate : float
            Total mass flowrate through reactor (g/s).
        power_levels : array [:math:`N_{steps}` x1]
            Normalized power level for each depletion step (W).
        depl_hist : array [:math:`N_{steps}` x1]
            Cumulative depletion time (d).

        """
        # initialize all object attributes
        self.volume = volume
        self.mass_flowrate = mass_flowrate
        self.power_levels = power_levels
        self.depl_hist = depl_hist
