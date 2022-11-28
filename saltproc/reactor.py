class Reactor ():
    """
    Class contains information about current state of the reactor.
    """

    def __init__(self,
                 volume=1.0,
                 mass_flowrate=0.0,
                 power_levels=[0.0],
                 depletion_steps=[1],
                 timestep_type='stepwise',
                 timestep_units='d'):
        """Initializes the class.

        Parameters
        ----------
        volume : float
            Total volume of the reactor core (:math:`cm^3`).
        mass_flowrate : float
            Total mass flowrate through reactor core (g/s).
        power_levels : array [:math:`N_{steps}` x1]
            Normalized power level for each depletion step (W).
        depletion_timesteps : array [:math:`N_{steps}` x1]
            Array of timesteps.
        timestep_type: str
            'cumulative', 'stepwise'.
        timestep_units : str
            Timestep units

        """
        # initialize all object attributes
        self.volume = volume
        self.mass_flowrate = mass_flowrate
        self.power_levels = power_levels
        self.depletion_timesteps = depletion_timesteps
        self.dep_step_units = dep_step_units
