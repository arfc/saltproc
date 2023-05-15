import sys
import subprocess
import shutil

from abc import ABC, abstractmethod

try:
    from mpi4py import MPI
    import os
    MPI_ON = True
except ImportError:
    MPI_ON = False


class Depcode(ABC):
    """Abstract interface for running depletion steps.

    Parameters
    ----------
    output_path : str
        Path to results storage directory.
    codename : str
        Name of depletion code.
    exec_path : str
        Path to depletion code executable.
    template_input_file_path : str or dict of str to str
        Path(s) to depletion code input file(s), or a dictionary where
        the input type (e.g. material, geometry, settings, etc.) as a
        string are keys, and the path to the input file are values.
        Type depends on depletion code in use.
    geo_file_paths : str or list, optional
        Path to file that contains the reactor geometry.
        List of `str` if reactivity control by
        switching geometry is `On` or just `str` otherwise.

    Attributes
    -----------
    neutronics_parameters : dict of str to type
        Holds depletion step neutronics parameters. Parameter names are keys
        and parameter values are values.
    step_metadata : dict of str to type
        Holds depletion code depletion step metadata. Metadata labels are keys
        and metadata values are values.
    runtime_inputfile : str
        Path to input file used to run depletion step.
    runtime_matfile : str
        Path to material file containing burnable materials used to
        run depletion step.
    npop : int
        Size of neutron population per cycle
    active_cycles : int
        Number of active cycles.
    inactive_cycles : int
        Number of inactive cycles.

    """

    def __init__(self,
                 codename,
                 output_path,
                 exec_path,
                 template_input_file_path,
                 geo_file_paths):
        """Initialize a Depcode object.

        """
        self.codename = codename
        self.output_path = output_path
        self.exec_path = exec_path
        self.template_input_file_path = template_input_file_path
        self.geo_file_paths = geo_file_paths
        self.neutronics_parameters = {}
        self.step_metadata = {}
        self.runtime_inputfile = None
        self.runtime_matfile = None

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
    def read_depleted_materials(self, read_at_end=False):
        """Reads depleted materials from the depletion step results
        and returns a dictionary containing them.

        Parameters
        ----------
        read_at_end : bool, optional
            If `True`, the function reads data at the end of the
            depletion step. Otherwise, the function reads data at the
            beginning of the depletion step.

        Returns
        -------
        depleted_materials : dict of str to Materialflow
            Dictionary containing depleted materials.

            ``key``
                Name of burnable material.
            ``value``
                :class:`Materialflow` object holding material composition and properties.

        """
    def run_depletion_step(self, mpi_args, args):
        """Runs a depletion step as a subprocess with the given parameters.

        Parameters
        ----------
        mpi_args : list of str
            Arguments for running simulations on supercomputers using
            ``mpiexec`` or similar programs.
        args : list of str
            Arguments for running depletion step.

        """

        print('Running %s' % (self.codename))
        try:
            if MPI_ON:
                env = os.environ
            else:
                env = None
            subprocess.run(
                args,
                check=True,
                cwd=self.output_path,
                stdout=sys.stdout,
                stderr=subprocess.STDOUT,
                env=env)
            print(f'Finished {self.codename.upper()} Run')
        except subprocess.CalledProcessError as error:
            print(error.output.decode("utf-8"))
            raise RuntimeError('\n %s RUN FAILED\n see error message above'
                               % (self.codename))

    @abstractmethod
    def switch_to_next_geometry(self):
        """Changes the geometry used in the depletion code simulation to the
        next geometry file in ``geo_file_paths``
        """

    @abstractmethod
    def write_runtime_input(self, reactor, dep_step, restart):
        """Write input file(s) for running depletion step

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
    def update_depletable_materials(self, mats, dep_end_time):
        """Update material file with reprocessed material compositions.

        Parameters
        ----------
        mats : dict of str to Materialflow
            Dictionary containing reprocessed material compositions.

            ``key``
                Name of burnable material.
            ``value``
                :class:`Materialflow` object holding composition and properties.
        dep_end_time : float
            Current time at the end of the depletion step (d).

        """

    def read_plaintext_file(self, file_path):
        """Reads the content of a plaintext file for use by other methods.

        Parameters
        ----------
        file_path : str
            Path to file.

        Returns
        -------
        file_lines : list of str
            File lines.

        """
        file_lines = []
        with open(file_path, 'r') as file:
            file_lines = file.readlines()
        return file_lines

    @abstractmethod
    def nuclide_code_to_name(self, nuc_code):
        """Converts depcode nuclide code to symbolic nuclide name.

        Parameters
        ----------
        nuc_code : str
            Nuclide code

        Returns
        -------
        nuc_name : str
            Symbolic nuclide name (`Am242m1`).

        """

    @abstractmethod
    def name_to_nuclide_code(self, nucname):
        """Converts depcode nuclide name to ZA nuclide code

        Parameters
        ----------
        nucname : str
            Nuclide namce

        Returns
        -------
        nuc_name : str
            ZA nuclide code

        """

    def preserve_simulation_files(self, step_idx):
        """Move simulation input and output files
        to unique a directory

        Parameters
        ----------
        step_idx : int

        """
        step_results_dir = self.output_path / f'step_{step_idx}_data'
        step_results_dir.mkdir(exist_ok=True)

        file_path = lambda file : self.output_path / file
        output_paths = list(map(file_path, self._OUTPUTFILE_NAMES))
        input_paths = list(map(file_path, self._INPUTFILE_NAMES))
        for file_path, fname in zip(output_paths, self._OUTPUTFILE_NAMES):
            file_path.rename(step_results_dir / fname)

        for file_path, fname in zip(input_paths, self._INPUTFILE_NAMES):
            lines = self.read_plaintext_file(file_path)
            with open(step_results_dir / fname, 'w') as out_file:
                out_file.writelines(lines)

    def rebuild_simulation_files(self, step_idx):
        """Move simulation input and output files
        from unique directory to runtime directory

        Parameters
        ----------
        step_idx : int

        """
        step_results_dir = self.output_path / f'step_{step_idx}_data'

        file_path = lambda file : self.output_path / step_results_dir / file
        output_paths = list(map(file_path, self._OUTPUTFILE_NAMES))
        input_paths = list(map(file_path, self._INPUTFILE_NAMES))
        for file_path, fname in zip(output_paths, self._OUTPUTFILE_NAMES):
            shutil.copy(file_path, (self.output_path / fname))

        for file_path, fname in zip(input_paths, self._INPUTFILE_NAMES):
            shutil.copy(file_path, (self.output_path / fname))
