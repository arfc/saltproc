class Depcode():
    """ Class contains information about input, output, geometry, and template
    file for running depletion simulation code. Also contains information about
     neutrons population, active and inactive cycle, etc.
    """

    def __init__(
                self,
                codename,
                template_filename,
                input_filename,
                output_filename,
                npop,
                active_cycles,
                inactive_cycles):
            """ Initializes the class

            Parameters:
            -----------
            codename: string
                name of the code for depletion
            template_filename: string
                name of user input file for depletion code with geometry and
                 initial composition
            input_filename: string
                name of input file for depletion code rerunning
            output_filename: string
                name of output file for depletion code rerunning
            npop: int
                size of neutron population for Monte-Carlo code
            active_cycles: int
                number of active cycles
            inactive_cycles: int
                number of inactive cycles
            """
