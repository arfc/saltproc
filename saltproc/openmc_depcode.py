import subprocess
import os
import shutil
import re
import json
from pathlib import Path
import numpy as np

from pyne import nucname as pyname
from pyne import serpent
import openmc

from saltproc import Materialflow
from saltproc.abc import Depcode
from openmc.deplete.abc import _SECONDS_PER_DAY
from openmc.deplete import Results
from openmc.data import atomic_mass

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
                 geo_file_paths,
                 depletion_settings,
                 chain_file_path
                 ):
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
           geo_file_paths : str or list, optional
               Path to file that contains the reactor geometry.
               List of `str` if reactivity control by
               switching geometry is `On` or just `str` otherwise.
            depletion_settings : dict
                Keyword arguments to pass to :func:`openmc.model.deplete()`.
            chain_file_path : str
                Path to depletion chain file

        """

        # if using the default depletion file, make sure we have the right path
        if exec_path == "openmc_deplete.py":
            exec_path = (Path(__file__).parents[0] / exec_path).resolve()
        else:
            exec_path == (Path(template_input_file_path['settings'].parents[0]) / exec_path).resolve()

        self.depletion_settings = depletion_settings
        self.chain_file_path = chain_file_path

        super().__init__("openmc",
                         output_path,
                         exec_path,
                         template_input_file_path,
                         geo_file_paths)
        self.runtime_inputfile = \
            {'geometry': str((output_path / 'geometry.xml').resolve()),
             'settings': str((output_path / 'settings.xml').resolve())}
        self.runtime_matfile = str((output_path / 'materials.xml').resolve())

        self._check_for_material_names(self.runtime_matfile)

    def _check_for_material_names(self, filename):
        """Checks that all materials in the material file
        have a name.

        Parameters
        ----------
        filename : str
           Path to a materials.xml file

        """

        materials = openmc.Materials.from_xml(filename)

        material_id_to_name = {}
        for material in materials:
            if material.name == '':
                raise ValueError(f"Material {material.id} has no name.")


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
        # Determine moment in depletion step to read data from
        if read_at_end:
            moment = 1
        else:
            moment = 0

        results_file = Path(self.output_path / 'depletion_results.h5')
        depleted_materials = {}
        results = Results(results_file)
        #self.days = results['DAYS'][moment]
        depleted_openmc_materials = results.export_to_materials(moment)
        if read_at_end:
            starting_openmc_materials = results.export_to_materials(0)
        else:
            # placeholder for starting materials
            starting_openmc_materials = np.zeros(len(depleted_openmc_materials))

        openmc_materials = zip(starting_openmc_materials, depleted_openmc_materials)

        depleted_materials = {}
        for starting_material, depleted_material in openmc_materials:
            nucvec = self.create_mass_percents_dictionary(depleted_material)
            name = depleted_material.name
            depleted_materials[name] = Materialflow(nucvec)
            depleted_materials[name].mass = depleted_material.get_mass()
            depleted_materials[name].vol = depleted_material.volume
            depleted_materials[name].density = material.get_mass() / material.volume

            if read_at_end:
                starting_heavy_metal_mass = starting_material.fissionable_mass
                depleted_heavy_metal_mass = depleted_material.fissionable_mass
                power = resuts[1].source_rate
                days = np.diff(results[1].time)[0] / _SECONDS_PER_DAY
                burnup = power * days / (starting_heavy_metal_mass - depleted_heavy_metal_mass)
            else:
                burnup = 0
            depleted_materials[name].burnup = burnup
        return depleted_materials

    def _create_mass_percents_dictionary(self, mat):
        """Creates a dicitonary with nuclide codes
        in zzaaam formate as keys, and material composition
        in mass percent as values

        Parameters
        ----------
        mat : openmc.Material
            A material

        Returns
        -------
            mass_dict : dict of int to float
        """
        at_percents = []
        nucs = []
        at_mass = []
        for nuc, pt, tp in mat.nuclides:
            nucs.append(nuc)
            at_percents.append(pt)
            at_mass.append(atomic_mass(nuc))

        at_percents = np.array(at_percents)
        at_mass = np.array(at_mass)

        mass_percents = at_percents*at_mass / np.dot(at_percents, at_mass)
        zai = list(map(openmc.data.zam, nucs))
        zam = list(map(self._z_a_m_to_zam, zai))

        return dict(zip(zam, mass_percents))

    def _z_a_m_to_zam(self,z_a_m_tuple):
        """Helper function for :func:`_create_mass_percents_dictionary`.
        Converts an OpenMC (Z,A,M) tuple into a zzaaam nuclide code

        Parameters
        ----------
        z_a_m_tuple : 3-tuple of int
            (z, a, m)

        Returns
        -------
            zam : int
            Nuclide code in zzaaam format

        """
        z, a, m = z_a_m_tuple
        zam = 1000 * z
        zam += a
        if m > 0 and (z != 95 and a != 242):
            zam += 300 + 100 * m
        elif z == 95 and a == 242:
            if m == 0:
              zam = 95642
            else:
              zam = 95242
        return zam


    def run_depletion_step(self, mpi_args=None, threads=None):
        """Runs a depletion step in OpenMC as a subprocess

        mpi_args : list of str
            Arguments for running simulations on supercomputers using
            ``mpiexec`` or similar programs.
        threads : int
            Threads to use for shared-memory parallelism

        """
        # need to add flow control for plots option
        args = ['python',
                self.exec_path,
                '--materials',
                self.runtime_matfile,
                '--geometry',
                self.runtime_inputfile['geometry'],
                '--settings',
                self.runtime_inputfile['settings'],
                '--tallies',
                self.runtime_inputfile['tallies'],
                '--directory',
                str(self.output_path)]
        if mpi_args is not None:
            args = mpi_args + args

        print('Running %s' % (self.codename))
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
        the next geometry file in `geo_file_paths`.
        """
        mats = openmc.Materials.from_xml(self.runtime_matfile)
        next_geometry = openmc.Geometry.from_xml(
            path=self.geo_file_paths.pop(0),
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
                self.geo_file_paths[0], materials=materials)
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
        """Write the depeletion settings for the ``openmc.deplete``
        module.

        Parameters
        ----------
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        step_idx : int
            Current depletion step.

        """
        current_power = reactor.power_levels[step_idx]

        # Get current depletion step length
        step_length = reactor.depletion_timesteps[step_idx]

        self.depletion_settings['directory'] = str(self.output_path)
        self.depletion_settings['timesteps'] = [step_length]

        operator_kwargs = {}
        input_path = Path(self.template_input_file_path['materials']).parents[0]
        try:
            if not(operator_kwargs['fission_q'] is None):
                operator_kwargs['fission_q'] = \
                    (input_path / operator_kwargs['fission_q']).resolve().as_posix()
        except KeyError:
            pass
        operator_kwargs['chain_file'] = self.chain_file_path

        self.depletion_settings['operator_kwargs'].update(operator_kwargs)

        integrator_kwargs = {}
        integrator_kwargs['power'] = current_power
        integrator_kwargs['timestep_units'] = reactor.timestep_units
        self.depletion_settings['integrator_kwargs'].update(integrator_kwargs)

        with open(self.output_path / 'depletion_settings.json', 'w') as f:
            depletion_settings_json = json.dumps(self.depletion_settings, indent=4)
            f.write(depletion_settings_json)

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


