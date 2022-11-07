from abc import ABC, abstractmethod

class Depcode(ABC):
    """Abstract class for interfacing with monte-carlo particle transport
    codes. Contains information about input, output, geometry, and template
    files for running depletion simulations. Also contains neutron
    population, active, and inactive cycles. Contains methods to read template
    and output files, and write new input files for the depletion code.

    Attributes
    -----------
    neutronics_parameters : dict of str to type
        Holds depletion step neutronics parameters. Parameter names are keys
        and parameter values are values.
    step_metadata : dict of str to type
        Holds depletion code depletion step metadata. Metadata labels are keys
        and metadata values are values.
    iter_inputfile : str
        Path to depletion code input file for depletion code rerunning.
    iter_matfile : str
        Path to iterative, rewritable material file for depletion code
        rerunning. This file is modified during  the simulation.

    """

    def __init__(self,
                 codename,
                 exec_path,
                 template_input_file_path,
                 geo_files=None,
                 npop=50,
                 active_cycles=20,
                 inactive_cycles=20):
        """Initializes the Depcode object.

           Parameters
           ----------
           codename : str
               Name of depletion code.
           exec_path : str
               Path to depletion code executable.
           template_input_file_path : str or dict of str to str
               Path(s) to depletion code input file(s), or a dictionary where
               the input type (e.g. material, geometry, settings, etc.) as a
               string are keys, and the path to the input file are values.
               Type depends on depletion code in use.
           geo_files : str or list, optional
               Path to file that contains the reactor geometry.
               List of `str` if reactivity control by
               switching geometry is `On` or just `str` otherwise.
           npop : int, optional
               Size of neutron population per cycle for Monte Carlo.
           active_cycles : int, optional
               Number of active cycles.
           inactive_cycles : int, optional
               Number of inactive cycles.

        """
        self.codename = codename
        self.exec_path = exec_path
        self.template_input_file_path = template_input_file_path
        self.geo_files = geo_files
        self.npop = npop
        self.active_cycles = active_cycles
        self.inactive_cycles = inactive_cycles
        self.neutronics_parameters = {}
        self.step_metadata = {}
        self.iter_inputfile = './iter_input'
        self.iter_matfile = './iter_mat'

    @abstractmethod
    def read_step_metadata(self):
        """Reads depletion code's depletion step metadata and stores it in the
        :class:`Depcode` object's :attr:`step_metadata` attribute.
        """

    @abstractmethod
    def read_neutronics_parameters(self):
        """Reads depletion code's depletion step neutronics parameters and
        stores them in :class:`Depcode` object's
        :attr:`neutronics_parameters` attribute.
        """

    @abstractmethod
    def read_dep_comp(self, read_at_end=False):
        """Reads the depleted material data from the depcode simulation
        and returns a dictionary with a `Materialflow` object for each
        burnable material.

        Parameters
        ----------
        read_at_end : bool, optional
            Controls at which moment in the depletion step to read the data.
            If `True`, the function reads data at the end of the
            depletion step. Otherwise, the function reads data at the
            beginning of the depletion step.

        Returns
        -------
        mats : dict of str to Materialflow
            Dictionary that contains `Materialflow` objects.

            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.

        """

    @abstractmethod
    def run_depcode(self, cores, nodes):
        """Runs depletion code as a subprocess with the given parameters.

        Parameters
        ----------
        cores : int
            Number of cores to use for depletion code run.
        nodes : int
            Number of nodes to use for depletion code run.
        """

    @abstractmethod
    def switch_to_next_geometry(self):
        """Changes the geometry used in the depletion code simulation to the
        next geometry file in ``geo_files``
        """

    @abstractmethod
    def write_depcode_input(self, reactor, dep_step, restart):
        """ Writes prepared data into depletion code input file(s).

        Parameters
        ----------
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        dep_step : int
            Current depletion time step.
        restart : bool
            Is the current simulation restarted?
        """

    @abstractmethod
    def write_mat_file(self, dep_dict, dep_end_time):
        """Writes the iteration input file containing the burnable materials
        composition used in depletion runs and updated after each depletion
        step.

        Parameters
        ----------
        dep_dict : dict of str to Materialflow
            Dictionary that contains `Materialflow` objects.

            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.
        dep_end_time : float
            Current time at the end of the depletion step (d).

        """



