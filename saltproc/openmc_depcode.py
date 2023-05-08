import subprocess
import os
import re
import json
from pathlib import Path
import numpy as np

from uncertainties import unumpy
import openmc

from saltproc import Materialflow
from saltproc.depcode import Depcode
from openmc.deplete.abc import _SECONDS_PER_DAY
from openmc.deplete import Results, Chain, MicroXS
from openmc.mgxs import Beta, DecayRate, EnergyGroups
from openmc.data import atomic_mass, DataLibrary, JOULE_PER_EV


_FISSILE_NUCLIDES = ['U233', 'U235', 'Pu239', 'Pu241']
_FERTILE_NUCLIDES = ['Th232', 'U234', 'U238', 'Pu238', 'Pu240']
_KG_PER_G = 1e-3
_MW_PER_W = 1e-6
_DELAYED_ENERGY_BOUNDS = (0,20e7) # eV
_N_DELAYED_GROUPS = 6

class OpenMCDepcode(Depcode):
    """Interface for running depletion steps in OpenMC, as well as obtaining
    depletion step results.

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

        self._check_for_material_names(self.template_input_file_path['materials'])

        self._OUTPUTFILE_NAMES = ('depletion_results.h5', 'openmc_simulation_n0.h5',
                                 'openmc_simulation_n1.h5', 'summary.h5',
                                 'tallies.out')
        self._INPUTFILE_NAMES = ('materials.xml', 'geometry.xml', 'tallies.xml')

    def _check_for_material_names(self, filename):
        """Checks that all materials in the material file
        have a name.

        Parameters
        ----------
        filename : str
           Path to a materials.xml file

        """

        openmc.reset_auto_ids()
        materials = openmc.Materials.from_xml(filename)

        material_id_to_name = {}
        for material in materials:
            if material.name == '':
                raise ValueError(f"Material {material.id} has no name.")

    def read_step_metadata(self):
        """Reads OpenMC's depletion step metadata and stores it in the
        :class:`OpenMCDepcode` object's :attr:`step_metadata` attribute.
        """
        sp0 = openmc.StatePoint(self.output_path / 'openmc_simulation_n0.h5')
        sp1 = openmc.StatePoint(self.output_path / 'openmc_simulation_n1.h5')
        res = Results(self.output_path / 'depletion_results.h5')

        depcode_name, depcode_ver = self.codename, ".".join(list(map(str,sp0.version)))
        execution_time = sp0.runtime['simulation'] + sp1.runtime['simulation'] + res[0].proc_time + res[1].proc_time
        sp0.close()
        sp1.close()

        self.step_metadata['depcode_name'] = depcode_name
        self.step_metadata['depcode_version'] = depcode_ver
        self.step_metadata['title'] = ''
        self.step_metadata['depcode_input_filename'] = ''
        self.step_metadata['depcode_working_dir'] = str(self.output_path)
        self.step_metadata['xs_data_path'] = self._find_xs_path()
        self.step_metadata['OMP_threads'] = -1
        self.step_metadata['MPI_tasks'] = -1
        self.step_metadata['memory_optimization_mode'] = -1
        self.step_metadata['depletion_timestep'] = res[1].time[0]
        self.step_metadata['execution_time'] = execution_time
        self.step_metadata['memory_usage'] = -1

    def _find_xs_path(self):
        try:
            xs_path = os.environ['OPENMC_CROSS_SECTIONS']
        except KeyError:
            openmc.reset_auto_ids()
            xs_path = openmc.Materials.from_xml(self.runtime_matfile).cross_sections
        return xs_path

    def read_neutronics_parameters(self):
        """Reads OpenMC depletion step neutronics parameters and stores them
        in :class:`OpenMCDepcode` object's :attr:`neutronics_parameters`
        attribute.
        """
        sp0 = openmc.StatePoint(self.output_path / 'openmc_simulation_n0.h5')
        sp1 = openmc.StatePoint(self.output_path / 'openmc_simulation_n1.h5')
        res = Results(self.output_path / 'depletion_results.h5')

        self.neutronics_parameters['keff_bds'] = res[0].k[0]
        self.neutronics_parameters['keff_eds'] = res[1].k[0]
        self.neutronics_parameters['breeding_ratio'] = self._calculate_breeding_ratio(sp1)
        self.neutronics_parameters['burn_days'] = res[1].time[0] / _SECONDS_PER_DAY
        self.neutronics_parameters['power_level'] = res[1].source_rate
        self.neutronics_parameters['beta_eff'] = self._calculate_delayed_quantity(sp1, self._beta)
        self.neutronics_parameters['delayed_neutrons_lambda'] = \
            self._calculate_delayed_quantity(sp1, self._delayed_lambda)
        init_fission_mass, final_fission_mass = self._calculate_fission_masses(res)
        self.neutronics_parameters['fission_mass_bds'] = init_fission_mass
        self.neutronics_parameters['fission_mass_eds'] = final_fission_mass
        del sp0, sp1

    def _calculate_breeding_ratio(self, sp1):
        """Fissile material produces / fissile material destroyed"""

        breeding_ratio_tally = sp1.get_tally(name='breeding_ratio_tally')
        frame = breeding_ratio_tally.get_pandas_dataframe().set_index('score')
        n_gamma_frame = frame.loc['(n,gamma)'].set_index('nuclide')
        absorption_frame = frame.loc['absorption'].set_index('nuclide')

        n_gamma_vals = self._get_values_with_uncertainties(n_gamma_frame)
        absorption_vals = self._get_values_with_uncertainties(absorption_frame)

        n_gamma_series = dict(zip(n_gamma_frame.index, n_gamma_vals))
        absorption_series = dict(zip(absorption_frame.index, absorption_vals))

        fissionable_production_rate = np.sum([n_gamma_series[nuc] for nuc in self._fertile_nucs])
        fissionable_destruction_rate = np.sum([absorption_series[nuc] for nuc in self._fissile_nucs])

        breeding_ratio = fissionable_production_rate / fissionable_destruction_rate

        return np.array([breeding_ratio.n, breeding_ratio.s])

    def _calculate_delayed_quantity(self, sp1, mgxs):
        # group-wise delayed quantity
        mgxs.load_from_statepoint(sp1)
        frame = mgxs.get_pandas_dataframe()
        vals = self._get_values_with_uncertainties(frame)
        tot = vals.sum()
        vals = [[v.n, v.s] for v in vals]
        tot = np.array([[tot.n, tot.s]])

        return np.concatenate([tot, vals])

    def _get_values_with_uncertainties(self, frame):
        vals = np.array(list(zip(frame['mean'], frame['std. dev.'])))
        return unumpy.uarray(frame['mean'], frame['std. dev.'])

    def _calculate_fission_masses(self, res):
        """Calculate the fission mass [kg] before and after material depletion"""
        init_fission_mass = 0
        final_fission_mass = 0
        init_mats = res.export_to_materials(0)
        final_mats = res.export_to_materials(1)
        for init_mat, final_mat in zip(init_mats, final_mats):
            if init_mat.depletable:
                init_fission_mass += init_mat.fissionable_mass
            if final_mat.depletable:
                final_fission_mass += final_mat.fissionable_mass

        # Convert g to kg
        init_fission_mass *= _KG_PER_G
        final_fission_mass *= _KG_PER_G

        del init_mat, final_mat, init_mats, final_mats
        return init_fission_mass, final_fission_mass

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
        depleted_openmc_materials = results.export_to_materials(moment)
        if read_at_end:
            starting_openmc_materials = results.export_to_materials(0)
        else:
            # placeholder for starting materials
            starting_openmc_materials = np.zeros(len(depleted_openmc_materials))

        openmc_materials = zip(starting_openmc_materials, depleted_openmc_materials)

        depleted_materials = {}
        for starting_material, depleted_material in openmc_materials:
            if depleted_material.depletable:
                volume = depleted_material.volume
                density = depleted_material.get_mass_density()
                comp = self._create_mass_percents_dictionary(depleted_material)
                name = depleted_material.name
                if read_at_end:
                    sp0 = openmc.StatePoint(self.output_path / 'openmc_simulation_n0.h5')
                    heavy_metal_mass = starting_material.fissionable_mass * _KG_PER_G
                    power = results[1].source_rate * _MW_PER_W
                    days = results[1].time[1] / _SECONDS_PER_DAY
                    burnup = power * days / heavy_metal_mass
                else:
                    burnup = 0
                depleted_materials[name] = Materialflow(comp=comp,
                                                        density=density,
                                                        volume=volume,
                                                        burnup=burnup)
        del openmc_materials, depleted_openmc_materials, starting_openmc_materials
        return depleted_materials

    def _create_mass_percents_dictionary(self, mat, percent_type='ao'):
        """Creates a dicitonary with nuclide codes
        in zzaaam formate as keys, and material composition
        in mass percent as values

        Parameters
        ----------
        mat : openmc.Material
            A material
        percent_type : str
            Percent type of material

        Returns
        -------
            mass_dict : dict of int to float
        """
        percents = np.zeros(len(mat.nuclides))
        nucs = []
        at_mass = np.zeros(len(mat.nuclides))
        for i, (nuc, pt, tp) in enumerate(mat.nuclides):
            nucs.append(nuc)
            percents[i] = pt
            at_mass[i] = atomic_mass(nuc)

        if percent_type == 'ao':
            mass_percents = percents*at_mass / np.dot(percents, at_mass)
        elif percent_type == 'wo':
            mass_percents = percents
        else:
            raise ValueError(f'{percent_type} is not a valid percent type')

        return dict(zip(nucs, mass_percents))

    def _get_power_from_tallies(self, sp, power):
        fission_energy = sp.get_tally(name='fission_energy').mean.flatten()[0] # eV / src
        heating = sp.get_tally(name='heating').mean.flatten()[0] # eV / src
        Hp = JOULE_PER_EV * heating # J / src
        f = power / Hp # src / s
        power = fission_energy * f * JOULE_PER_EV # J / s
        return power

    def nuclide_code_to_name(self, nuc):
        return nuc

    def name_to_nuclide_code(self, nucname):
        z, a, m = openmc.data.zam(nucname)
        code = z * 1000 + a
        if m != 0:
            code += 300 + 100 * m
        return code

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
                str(self.exec_path),
                '--materials',
                str(self.runtime_matfile),
                '--geometry',
                str(self.runtime_inputfile['geometry']),
                '--settings',
                str(self.runtime_inputfile['settings']),
                '--tallies',
                str(self.runtime_inputfile['tallies']),
                '--directory',
                str(self.output_path)]
        if mpi_args is not None:
            args = mpi_args + args

        super().run_depletion_step(mpi_args, args)

    def switch_to_next_geometry(self):
        """Switches the geometry file for the OpenMC depletion simulation to
        the next geometry file in `geo_file_paths`.
        """
        openmc.reset_auto_ids()
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
            geo_file = self.geo_file_paths.pop(0)
            openmc.reset_auto_ids()
            materials = openmc.Materials.from_xml(
                self.template_input_file_path['materials'])
            geometry = openmc.Geometry.from_xml(
                geo_file, materials=materials)
            settings = openmc.Settings.from_xml(
                self.template_input_file_path['settings'])
            self.npop = settings.particles
            self.inactive_cycles = settings.inactive
            self.active_cycles = settings.batches - self.inactive_cycles

        else:
            openmc.reset_auto_ids()
            materials = openmc.Materials.from_xml(self.runtime_matfile)
            geometry = openmc.Geometry.from_xml(
                self.runtime_inputfile['geometry'], materials=materials)
            settings = openmc.Settings.from_xml(
                self.runtime_inputfile['settings'])

        diluted_model = openmc.Model(materials=materials, geometry=geometry, settings=settings)
        reactions, diluted_materials = MicroXS._add_dilute_nuclides(self.chain_file_path,
                                                                   diluted_model,
                                                                   1e3)

        diluted_materials.export_to_xml(self.runtime_matfile)
        geometry.export_to_xml(self.runtime_inputfile['geometry'])
        settings.export_to_xml(self.runtime_inputfile['settings'])
        self.write_depletion_settings(reactor, depletion_step)
        self.write_saltproc_openmc_tallies(materials, geometry, _DELAYED_ENERGY_BOUNDS, _N_DELAYED_GROUPS)
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
        openmc.reset_auto_ids()
        runtime_materials = openmc.Materials.from_xml(self.runtime_matfile)

        for material in runtime_materials:
            # depletable materials only
            if material.name in mats.keys():
                components = {}
                for nuc_name, mass_fraction in mats[material.name].comp.items():
                    components[nuc_name] = mass_fraction

                material.set_density('g/cm3', mats[material.name].density)
                material.volume = mats[material.name].volume
                for element in material.get_elements():
                    material.remove_element(element)
                material.add_components(components, percent_type='wo')

        runtime_materials.export_to_xml(path=self.runtime_matfile)
        del runtime_materials
        del material


    def write_saltproc_openmc_tallies(self, materials, geometry, energy_bounds, n_delayed_groups):
        """
        Write tallies for calculating burnup and delayed neutron
        parameters.

        Parameters
        ----------
        materials : `openmc.Materials` object
            The materials for the depletion simulation
        geometry : `openmc.Geometry` object
            The geometry for the depletion simulation
        energy_bounds : iterable of float
            Energy group boundaries for calculating :math:`\\beta`, the delayed
            neutron fraction, and :math:`\\lambda`, the decay rate for delayed
            neutron precursors.
        n_delayed_groups : int
            Number of delayed groups for calculating :math:`\\beta`, the delayed
            neutron fraction, and :math:`\\lambda`, the decay rate for delayed
            neutron precursors.

        """

        ff_nuclides = self._get_fissile_fertile_nuclides()
        energy_groups = EnergyGroups(energy_bounds)
        delayed_groups = np.arange(1, n_delayed_groups + 1, 1).tolist()

        delayed_kwargs = {'domain': geometry.root_universe,
                          'domain_type': 'universe',
                          'energy_groups': energy_groups,
                          'delayed_groups': delayed_groups}

        delayed_lambda = DecayRate(**delayed_kwargs)
        beta = Beta(**delayed_kwargs)

        self._delayed_lambda = delayed_lambda
        self._beta = beta

        tallies = openmc.Tallies()
        tallies += list(delayed_lambda.tallies.values())
        tallies += list(beta.tallies.values())

        tally = openmc.Tally(name='breeding_ratio_tally')
        tally.filters = [openmc.UniverseFilter(geometry.root_universe)]
        tally.scores = ['(n,gamma)', 'absorption']
        tally.nuclides = ff_nuclides
        tallies.append(tally)

        tally = openmc.Tally(name='fission_energy')
        tally.filters = [openmc.UniverseFilter(geometry.root_universe)]
        tally.scores = ['kappa-fission']
        tallies.append(tally)

        tally = openmc.Tally(name='heating')
        tally.filters = [openmc.UniverseFilter(geometry.root_universe)]
        tally.scores = ['heating']
        tallies.append(tally)

        self.runtime_inputfile['tallies'] = self.output_path / 'tallies.xml'
        tallies.export_to_xml(self.runtime_inputfile['tallies'])

    def _get_fissile_fertile_nuclides(self):
        nuclides_with_data = set()
        data_lib = DataLibrary.from_xml()
        for library in data_lib.libraries:
            if library['type'] != 'neutron':
                continue
            for name in library['materials']:
                if name not in nuclides_with_data:
                    nuclides_with_data.add(name)

        chain = Chain.from_xml(self.chain_file_path)
        burnable_nucs = [nuc.name for nuc in chain.nuclides
                         if nuc.name in nuclides_with_data]

        self._fissile_nucs = set([nuc for nuc in _FISSILE_NUCLIDES if nuc in burnable_nucs])
        self._fertile_nucs = set([nuc for nuc in _FERTILE_NUCLIDES if nuc in burnable_nucs])

        return list(self._fissile_nucs.union(self._fertile_nucs))
