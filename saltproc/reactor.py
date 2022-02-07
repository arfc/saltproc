class Reactor ():
    """
    Class contains information about current state of the reactor.
    """

    def __init__(self,
                 volume=1.0,
                 mass_flowrate=0.0,
                 power_levels=[0.0],
                 dep_step_length_cumulative=[1]):
        """Initializes the class.

        Parameters
        ----------
        volume : float
            Total volume of the reactor core (:math:`cm^3`).
        mass_flowrate : float
            Total mass flowrate through reactor core (g/s).
        power_levels : array [:math:`N_{steps}` x1]
            Normalized power level for each depletion step (W).
        dep_step_length_cumulative : array [:math:`N_{steps}` x1]
            Cumulative depletion time (d).

        """
        # initialize all object attributes
        self.volume = volume
        self.mass_flowrate = mass_flowrate
        self.power_levels = power_levels
        self.dep_step_length_cumulative = dep_step_length_cumulative
