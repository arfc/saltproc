import subprocess
import os
import shutil
import re
import json

from pyne import nucname as pyname
from pyne import serpent
import openmc

from saltproc import Materialflow
from saltproc.abc import Depcode

class OpenMCDepcode(Depcode):
    """Interface for running depletion steps in OpenMC, as well as obtaining
    depletion step results.

    Attributes
    ----------
    neutronics_parameters : dict of str to type
        Holds OpenMC depletion step neutronics parameters. Parameter names are
        keys and parameter values are values.
    step_metadata : dict of str to type
        Holds OpenMC depletion step metadata. Metadata labels are keys
        and metadata values are values.
    runtime_inputfile : dict of str to str
        Paths to OpenMC input files used to run depletion step. Contains neutron
        settings and geometry.
    runtime_matfile : str
        Path to OpenMC material file containing materials used to
        run depletion step, and modified after fuel reprocessing.
    npop : int
        Size of neutron population per cycle
    active_cycles : int
        Number of active cycles.
    inactive_cycles : int
        Number of inactive cycles.

    """

    def __init__(self,
                 output_path,
                 exec_path,
                 template_input_file_path,
                 geo_files):
        """Initialize a OpenMCDepcode object.

           Parameters
           ----------
           output_path : str
               Path to results storage directory.
           exec_path : str
               Path to OpenMC depletion script.
           template_input_file_path : dict of str to str
               Path to user input files (``.xml`` file for geometry,
               material, and settings) for OpenMC. File type as strings
               are keys (e.g. 'geometry', 'settings', 'material'), and
               file path as strings are values.
           geo_files : str or list, optional
               Path to file that contains the reactor geometry.
               List of `str` if reactivity control by
               switching geometry is `On` or just `str` otherwise.

        """

        # if using the default depletion file, make sure we have the right path
        if exec_path == "openmc_deplete.py":
            exec_path = (Path(__file__).parents[0] / exec_path)

        super().__init__("openmc",
                         output_path,
                         exec_path,
                         template_input_file_path,
                         geo_files)
        self.runtime_inputfile = \
            {'geometry': (output_path / 'geometry.xml').resolve().as_posix(),
             'settings': (output_path / 'settings.xml').resolve().as_posix()}
        self.runtime_matfile = (output_path / 'materials.xml').resolve().as_posix()

    def read_step_metadata(self):
        """Reads OpenMC's depletion step metadata and stores it in the
        :class:`OpenMCDepcode` object's :attr:`step_metadata` attribute.
        """

    def read_neutronics_parameters(self):
        """Reads OpenMC depletion step neutronics parameters and stores them
        in :class:`OpenMCDepcode` object's :attr:`neutronics_parameters`
        attribute.
        """

    def read_depleted_materials(self, read_at_end=False):
        """Reads depleted materials from OpenMC's `depletion_results.h5` file
        and returns a dictionary with a :class:`Materialflow` object for each
        depleted material.

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
                :class:`Materialflow` object holding composition and properties.

        """

    def run_depletion_step(self, cores, nodes):
        """Runs a depletion step in OpenMC as a subprocess with the given
        parameters.

        Parameters
        ----------
        cores : int
            Number of cores to use for depletion code run.
        nodes : int
            Number of nodes to use for depletion code run.
        """
        # need to add flow control for plots option
        args = (
            'mpiexec',
            '-n',
            str(nodes),
            'python',
            self.exec_path
            '--materials',
            self.runtime_matfile,
            '--geometry',
            self.runtime_inputfile['geometry'],
            '--settings',
            self.runtime_inputfile['settings'],
            '--tallies',
            self.runtime_inputfile['tallies'],
            '--depletion_settings',
            self.runtime_inputfile['depletion_settings'])

        print('Running %s' % (self.codename))
        # TODO: Need to figure out how to adapt this to openmc
        try:
            subprocess.check_output(
                args,
                cwd=os.path.split(self.template_inputfile_path)[0],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print(error.output.decode("utf-8"))
            raise RuntimeError('\n %s RUN FAILED\n see error message above'
                               % (self.codename))
        print('Finished OpenMC Run')

    def switch_to_next_geometry(self):
        """Switches the geometry file for the OpenMC depletion simulation to
        the next geometry file in `geo_files`.
        """
        mats = openmc.Materials.from_xml(self.runtime_matfile)
        next_geometry = openmc.Geometry.from_xml(
            path=self.geo_files.pop(0),
            materials=mats)
        next_geometry.export_to_xml(path=self.runtime_inputfile['geometry'])
        del mats, next_geometry

    def write_runtime_input(self, reactor, depletion_step, restart):
        """Write OpenMC runtime input files for running depletion step.

        Parameters
        ----------
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        depletion_step : int
            Current depletion time step.
        restart : bool
            Is the current simulation restarted?
        """

        if depletion_step == 0 and not restart:
            materials = openmc.Materials.from_xml(
                self.template_input_file_path['materials'])
            geometry = openmc.Geometry.from_xml(
                self.geo_files[0], materials=materials)
            settings = openmc.Settings.from_xml(
                self.template_input_file_path['settings'])
            self.npop = settings.particles
            self.inactive_cycles = settings.inactive
            self.active_cycles = settings.batches - self.inactive_cycles

        else:
            materials = openmc.Materials.from_xml(self.runtime_matfile)
            geometry = openmc.Geometry.from_xml(
                self.runtime_inputfile['geometry'], materials=materials)
            settings = openmc.Settings.from_xml(
                self.runtime_inputfile['settings'])

        materials.export_to_xml(self.runtime_matfile)
        geometry.export_to_xml(self.runtime_inputfile['geometry'])
        settings.export_to_xml(self.runtime_inputfile['settings'])
        self.write_depletion_settings(reactor, depletion_step)
        self.write_saltproc_openmc_tallies(materials, geometry)
        del materials, geometry, settings

    def write_depletion_settings(self, reactor, step_idx):
        """Write the depeletion settings for the OpenMC depletion step.

        Parameters
        ----------
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        step_idx : int
            Current depletion step.

        """
        depletion_settings = {}
        current_power = reactor.power_levels[step_idx]

        # Get current depletion step length
        if step_idx == 0:
            step_length = reactor.dep_step_length_cumulative[0]
        else:
            step_length = \
                reactor.dep_step_length_cumulative[step_idx] - \
                reactor.dep_step_length_cumulative[step_idx - 1]

        out_path = os.path.dirname(self.runtime_inputfile['settings'])
        depletion_settings['directory'] = out_path
        depletion_settings['timesteps'] = [step_length]

        operator_kwargs = {}

        try:
            operator_kwargs['chain_file'] = \
                self.template_input_file_path['chain_file']
        except KeyError:
            raise SyntaxError("No chain file defined. Please provide \
            a chain file in your saltproc input file")

        integrator_kwargs = {}
        integrator_kwargs['power'] = current_power
        integrator_kwargs['timestep_units'] = 'd'  # days

        depletion_settings['operator_kwargs'] = operator_kwargs
        depletion_settings['integrator_kwargs'] = integrator_kwargs

        self.runtime_inputfile['depletion_settings'] = \
            os.path.join(out_path, 'depletion_settings.json')
        json_dep_settings = json.JSONEncoder().encode(depletion_settings)
        with open(self.runtime_inputfile['depletion_settings'], 'w') as f:
            f.writelines(json_dep_settings)

    def update_depletable_materials(self, mats, dep_end_time):
        """Updates material file with reprocessed material compositions.

        Parameters
        ----------
        mats : dict of str to Materialflow
            Dictionary containing reprocessed material compositions

            ``key``
                Name of burnable material.
            ``value``
                :class:`Materialflow` object holding composition and properties.
        dep_end_time : float
            Current time at the end of the depletion step (d).

        """

    def write_saltproc_openmc_tallies(self, materials, geometry):
        """
        Write tallies for calculating burnup and delayed neutron
        parameters.

        Parameters
        ----------
        materials : `openmc.Materials` object
            The materials for the depletion simulation
        geometry : `openmc.Geometry` object
            The geometry for the depletion simulation

        """
        tallies = openmc.Tallies()

        tally = openmc.Tally(name='delayed-fission-neutrons')
        tally.filters = [openmc.DelayedGroupFilter([1, 2, 3, 4, 5, 6])]
        tally.scores = ['delayed-nu-fission']
        tallies.append(tally)

        tally = openmc.Tally(name='total-fission-neutrons')
        tally.filters = [openmc.UniverseFilter(geometry.root_universe)]
        tally.scores = ['nu-fission']
        tallies.append(tally)

        tally = openmc.Tally(name='precursor-decay-constants')
        tally.filters = [openmc.DelayedGroupFilter([1, 2, 3, 4, 5, 6])]
        tally.scores = ['decay-rate']
        tallies.append(tally)

        tally = openmc.Tally(name='fission-energy')
        tally.filters = [openmc.UniverseFilter(geometry.root_universe)]
        tally.scores = [
            'fission-q-recoverable',
            'fission-q-prompt',
            'kappa-fission']
        tallies.append(tally)

        tally = openmc.Tally(name='normalization-factor')
        tally.filters = [openmc.UniverseFilter(geometry.root_universe)]
        tally.scores = ['heating']
        tallies.append(tally)

        out_path = os.path.dirname(self.runtime_inputfile['settings'])
        self.runtime_inputfile['tallies'] = \
            os.path.join(out_path, 'tallies.xml')
        tallies.export_to_xml(self.runtime_inputfile['tallies'])
        del tallies


