class Process():
    """ Class describes process which must be applied to Materialflow to change
     composition, direction, etc.
     """

    def __init__(
                self,
                mass_flowrate,
                inflow,
                outflow,
                efficency,
                volume):
            """ Initializes the class

            Parameters:
            -----------
            mat_name: string
                name of material from SERPENT input file

            """
