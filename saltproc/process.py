class Process():
    """ Class describes process which must be applied to Materialflow to change
     composition, direction, etc.
     """

    def __init__(
                self,
                mass_flowrate,
                capacity,
                volume,
                inflow,
                outflow,
                efficency):
            """ Initializes the class

            Parameters:
            -----------
            mass_flowrate: float
                mass flow rate of the material flow (g/s)
            capacity: float
                maximum mass flow rate of the material flow which current
                 process can handle (g/s)
            volume: float
                total volume of the current facility (cm**3)
            inflow: ndarray [ISO x number of inflows]
                array with isotope vectors from other processes and/or reactor
                 with mass moving into the current process (g)
            outflow: ndarray [ISO x number of inflows]
                array with isotope vectors from other processes and/or reactor
                 with mass moving from the current procces (g)
            efficency: ndarray [ISO x 1]
                vector contains removal efficency vector for the current
                 process (w.%)


            """
