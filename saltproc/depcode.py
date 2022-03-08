from saltproc import Materialflow
import subprocess
import os
import shutil
import re
from pyne import nucname as pyname
from pyne import serpent
import openmc
import json
from abc import ABC, abstractmethod


class Depcode(ABC):
    r"""Abstract class for interfacing with monte-carlo particle transport
    codes. Contains information about input, output, geometry, and template
    files for running depletion simulations. Also contains neutron
    population, active, and inactive cycles. Contains methods to read template
    and output files, and write new input files for the depletion code.

    Attributes
    -----------
    param : dict of str to type
        Holds depletion steo parameter information
    sim_info : dict of str to type
        Holds simulation settings information
    iter_inputfile : str
        Path to depletion code input file for depletion code rerunning.
    iter_matfile : str
        Path to iterative, rewritable material file for depletion code
        rerunning. This file is modified during  the simulation.

    """

    def __init__(self,
                 codename,
                 exec_path,
                 template_inputfiles_path,
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
           template_inputfiles_path: str or dict of str to str
               Path(s) to depletion code input file(s). Type depends
               on depletion code in use.
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
        self.template_inputfiles_path = template_inputfiles_path
        self.geo_files = geo_files
        self.npop = npop
        self.active_cycles = active_cycles
        self.inactive_cycles = inactive_cycles
        self.param = {}
        self.sim_info = {}
        self.iter_inputfile = './iter_input'
        self.iter_matfile = './iter_mat'

    @abstractmethod
    def read_depcode_info(self):
        """Parses initial depletion code info data from depletion code
        output and stores it in the `Depcode` object's ``sim_info`` attribute.
        """

    @abstractmethod
    def read_depcode_step_param(self):
        """Parses data from depletion code output for each step and stores
        it in `Depcode` object's ``param`` attributes.
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


class DepcodeOpenMC(Depcode):
    r"""Class contains information about input, output, geometry, and
    template files for running OpenMC depletion simulations.
    Also contains neutrons population, active, and inactive cycles.
    Contains methods to read template and output files,
    write new input files for OpenMC.

    Attributes:
    -----------
    param : dict of str to type
        Holds depletion steo parameter information
    sim_info : dict of str to type
        Holds simulation settings information
    iter_inputfile : dict of str to str
        Paths to OpenMC input files for OpenMC rerunning.
    iter_matfile : str
        Path to iterative, rewritable material file for OpenMC
        rerunning. This file is modified during the simulation.



    """

    def __init__(self,
                 exec_path="openmc_deplete.py",
                 template_inputfiles_path={"geometry": "./geometry.xml",
                                           "materials": "./materials.xml",
                                           "settings": "./settings.xml",
                                           "chain_file": "./chain_simple.xml"},
                 geo_files=None,
                 npop=50,
                 active_cycles=20,
                 inactive_cycles=20):
        """Initializes the DepcodeOpenMC object.

           Parameters
           ----------
           exec_path : str
               Path to OpenMC depletion script.
           template_inputfiles_path : dict of str to str
               Path to user input files (``.xml`` file for geometry,
               material, and settings) for OpenMC.
           iter_matfile : str
               Name of iterative, rewritable material file for OpenMC
               rerunning. This file is modified during  the simulation.
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
        super().__init__("openmc",
                         exec_path,
                         template_inputfiles_path,
                         geo_files,
                         npop,
                         active_cycles,
                         inactive_cycles)
        self.iter_inputfile = {'geometry': './geometry.xml',
                               'settings': './settings.xml'},
        self.iter_matfile = './materials.xml'

    def read_depcode_info(self):
        """Parses initial OpenMC simulation info from the OpenMC output files
        and stores it in the `Depcode` object's ``sim_info`` attribute.
        """

    def read_depcode_step_param(self):
        """Parses data from OpenMC depletion output for each step and stores
        it in `Depcode` object's ``param`` attributes.
        """

    def read_dep_comp(self, read_at_end=False):
        """Reads the depleted material data from the OpenMC depletion
        simulation and returns a dictionary with a `Materialflow` object for
        each burnable material.

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

    def run_depcode(self, cores, nodes):
        """Runs OpenMC depletion simulation as a subprocess with the given
        parameters.

        Parameters
        ----------
        cores : int
            Number of cores to use for depletion code run.
        nodes : int
            Number of nodes to use for depletion code run.
        """
        ## need to add flow control for plots option ##
        args = (
            'mpiexec',
            '-n',
            str(nodes),
            'python',
            './deplete_openmc.py'
            '-mat',
            self.iter_matfile,
            '-geo',
            self.iter_inputfile['geometry'],
            '-set',
            self.iter_inputfile['settings'],
            '-tal',
            self.iter_inputfile['tallies'],
            '-dep',
            self.iter_inputfile['depletion_settings'])

        print('Running %s' % (self.codename))
        # Need to figure out how to adapt this to openmc
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
        mats = openmc.Materials.from_xml(self.iter_matfile)
        next_geometry = openmc.Geometry.from_xml(
            path=self.geo_files.pop(0),
            materials=mats)
        next_geometry.export_to_xml(path=self.iter_inputfile['geometry'])
        del mats, next_geometry

    def write_depcode_input(self, reactor, dep_step, restart):
        """ Writes prepared data into OpenMC input file(s).

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

        if dep_step == 0 and not restart:
            materials = openmc.Materials.from_xml(
                self.template_inputfiles_path['materials'])
            geometry = openmc.Geometry.from_xml(
                self.template_inputfiles_path['geometry'], materials=materials)
            settings = openmc.Settings.from_xml(
                self.template_inputfiles_path['settings'])
            settings.particles = self.npop
            # settings.generations_per_batch = ??
            settings.inactive = self.inactive_cycles
            settings.batches = self.active_cycles + self.inactive_cycles
        else:
            materials = openmc.Materials.from_xml(self.iter_matfile)
            geometry = openmc.Geometry.from_xml(
                self.iter_inputfile['geometry'], materials=materials)
            settings = openmc.Settings.from_xml(
                self.iter_inputfile['settings'])

        materials.export_to_xml(self.iter_matfile)
        geometry.export_to_xml(self.iter_inputfile['geometry'])
        settings.export_to_xml(self.iter_inputfile['settings'])
        self.write_depletion_settings(reactor, dep_step)
        self.write_saltproc_openmc_tallies(materials, geometry)
        del materials, geometry, settings

    def write_depletion_settings(self, reactor, current_depstep_idx):
        """Write the depeletion settings for the ``openmc.depelete``
        module.

        Parameters
        ----------
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        current_depstep_idx : int
            Current depletion step.

        """
        depletion_settings = {}
        current_depstep_power = reactor.power_levels[current_depstep_idx]

        # Get current depletion step length
        if current_depstep_idx == 0:
            current_depstep = reactor.dep_step_length_cumulative[0]
        else:
            current_depstep = \
                reactor.dep_step_length_cumulative[current_depstep_idx] - \
                reactor.dep_step_length_cumulative[current_depstep_idx - 1]

        out_path = os.path.dirname(self.iter_inputfile['settings'])
        depletion_settings['directory'] = out_path
        depletion_settings['timesteps'] = [current_depstep]

        operator_kwargs = {}

        # Right now we'll require a path to the chain file.
        # In the future we can make this fanciet
        try:
            operator_kwargs['chain_file'] = \
                self.template_inputfiles_path['chain_file']
        except KeyError:
            raise SyntaxError("No chain file defined. Please provide \
            a chain file in your saltproc input file")

        integrator_kwargs = {}
        integrator_kwargs['power'] = current_depstep_power
        integrator_kwargs['timestep_units'] = 'd'  # days

        depletion_settings['operator_kwargs'] = operator_kwargs
        depletion_settings['integrator_kwargs'] = integrator_kwargs

        self.iter_inputfile['depletion_settings'] = \
            os.path.join(out_path, 'depletion_settings.json')
        json_dep_settings = json.JSONEncoder().encode(depletion_settings)
        with open(self.iter_inputfile['depletion_settings'], 'w') as f:
            f.writelines(json_dep_settings)

    def write_mat_file(self, dep_dict, dep_end_time):
        """Writes the iteration input file containing the burnable materials
        composition used in OpenMC depletion runs and updated after each
        depletion step.

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

        out_path = os.path.dirname(self.iter_inputfile['settings'])
        self.iter_inputfile['tallies'] = \
            os.path.join(out_path, 'tallies.xml')
        tallies.export_to_xml(self.iter_inputfile['tallies'])
        del tallies


class DepcodeSerpent(Depcode):
    r"""Class contains information about input, output, geometry, and
    template files for running Serpent2 depletion simulations.
    Also contains neutrons population, active, and inactive cycles.
    Contains methods to read template and output files,
    write new input files for Serpent2.

    Attributes
    -----------
    param : dict of str to type
        Holds Serpent depletion step parameter information
    sim_info : dict of str to type
        Holds Serpent simulation settings information
    iter_inputfile : str
        Path to Serpent2 input file for Serpent2 rerunning.
    iter_matfile : str
        Path to iterative, rewritable material file for Serpent2
        rerunning. This file is modified during the simulation.

    """

    def __init__(self,
                 exec_path="sss2",
                 template_inputfiles_path="reactor.serpent",
                 geo_files=None,
                 npop=50,
                 active_cycles=20,
                 inactive_cycles=20):
        """Initializes the DepcodeSerpent object.

           Parameters
           ----------
           exec_path : str
               Path to Serpent2 executable.
           template_inputfiles_path : str
               Path to user input file for Serpent2
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
        super().__init__("serpent",
                         exec_path,
                         template_inputfiles_path,
                         geo_files,
                         npop,
                         active_cycles,
                         inactive_cycles)
        self.iter_inputfile = './serpent_iter_input.serpent'
        self.iter_matfile = './serpent_iter_mat.ini'

    def change_sim_par(self, template_data):
        """Finds simulation parameters (neutron population, cycles) in the
        Serpent2 template file and change them to the parameters from the
        SaltProc input file.

        Parameters
        ----------
        template_data : list
            List of strings parsed from user's Serpent2 template file.

        Returns
        -------
        input_data : list
            List of strings containing Serpent2 input file with new
            simulation parameters.

        """
        if self.npop and self.active_cycles and self.inactive_cycles:
            sim_param = [s for s in template_data if s.startswith("set pop")]
            if len(sim_param) > 1:
                print('ERROR: Template file %s contains multiple lines with '
                      'simulation parameters:\n'
                      % (self.template_inputfiles_path), sim_param)
                return
            elif len(sim_param) < 1:
                print(
                    'ERROR: Template file %s does not contain line with '
                    'simulation parameters.' %
                    (self.template_inputfiles_path))
                return
            args = 'set pop %i %i %i\n' % (self.npop, self.active_cycles,
                                           self.inactive_cycles)
        return [s.replace(sim_param[0], args) for s in template_data]

    def create_iter_matfile(self, template_data):
        """Finds ``include`` line with path to material file, copies content of
        this file to iteration material file, changes path in ``include`` line
        to newly created iteration material file.

        Parameters
        ----------
        template_data : list
            List of strings parsed from user's template file.

        Returns
        -------
        input_data : list
            List of strings containing modified user template file.

        """
        data_dir = os.path.dirname(self.template_inputfiles_path)
        include_str = [s for s in template_data if s.startswith("include ")]
        if not include_str:
            print('ERROR: Template file %s has no <include "material_file">'
                  ' statements ' % (self.template_inputfiles_path))
            return
        src_file = include_str[0].split()[1][1:-1]
        if not os.path.isabs(src_file):
            abs_src_matfile = os.path.normpath(data_dir) + '/' + src_file
        else:
            abs_src_matfile = src_file
            if 'mat ' not in open(abs_src_matfile).read():
                print('ERROR: Template file %s has not include file with'
                      ' materials description or <include "material_file">'
                      ' statement is not appears'
                      ' as first <include> statement\n'
                      % (self.template_inputfiles_path))
                return
        # Create data directory
        try:
            os.mkdir(os.path.dirname(self.iter_matfile))
        except FileExistsError:
            pass
        # Create file with path for SaltProc rewritable iterative material file
        shutil.copy2(abs_src_matfile, self.iter_matfile)
        return [s.replace(src_file, self.iter_matfile) for s in template_data]

    def get_nuc_name(self, nuc_code):
        """Returns nuclide name in human-readable notation: chemical symbol
        (one or two characters), dash, and the atomic weight. Lastly, if the
        nuclide is in metastable state, the letter `m` is concatenated with
        number of excited state. For example, `Am-242m1`.

        Parameters
        ----------
        nuc_code : str
            Name of nuclide in Serpent2 form. For instance, `Am-242m`.

        Returns
        -------
        nuc_name : str
            Name of nuclide in human-readable notation (`Am-242m1`).
        nuc_zzaaam : str
            Name of nuclide in `zzaaam` form (`952421`).

        """

        if '.' in str(nuc_code):
            nuc_code = pyname.zzzaaa_to_id(int(nuc_code.split('.')[0]))
            zz = pyname.znum(nuc_code)
            aa = pyname.anum(nuc_code)
            aa_str = str(aa)
            # at_mass = pydata.atomic_mass(nuc_code_id)
            if aa > 300:
                if zz > 76:
                    aa_str = str(aa - 100) + 'm1'
                    aa = aa - 100
                else:
                    aa_str = str(aa - 200) + 'm1'
                    aa = aa - 200
                nuc_zzaaam = str(zz) + str(aa) + '1'
            elif aa == 0:
                aa_str = 'nat'
            nuc_name = pyname.zz_name[zz] + aa_str
        else:
            meta_flag = pyname.snum(nuc_code)
            if meta_flag:
                nuc_name = pyname.name(nuc_code)[:-1] + 'm' + str(meta_flag)
            else:
                nuc_name = pyname.name(nuc_code)
        nuc_zzaaam = \
            self.convert_nuclide_name_serpent_to_zam(pyname.zzaaam(nuc_code))
        return nuc_name, nuc_zzaaam

    def create_nuclide_name_map_zam_to_serpent(self):
        """ Create a map that accepts nuclide names in `zzaaam` format and
        returns the Serpent2 nuclide code format. Uses Serpent2 `*.out` file
        with list of all nuclides in simulation.

        Returns
        -------
        nuclide_map : dict of str to str
            Contains mapping for nuclide names from `zzaaam` to Serpent2
            format imported from Serpent2 ouput file:

            ``key``
                The key is nuclide name in `zzaaam` format. For example,
                `922350` or `982510`.
            ``value``
                Serpent2-oriented name. For instance, 92235.09c for transport
                isotope or 982510 for decay only isotope).

        """
        map_dict = {}
        # Construct path to the *.out File
        out_file = os.path.join('%s.out' % self.iter_inputfile)
        file = open(out_file, 'r')
        str_list = file.read().split('\n')
        # Stop-line
        end = ' --- Table  2: Reaction and decay data: '
        for line in str_list:
            if not line:
                continue
            if end in line:
                break
            if 'c  TRA' in line or 'c  DEC' in line:
                line = line.split()
                iname, zzaaam = self.get_nuc_name(line[2])
                map_dict.update({zzaaam: line[2]})
        self.iso_map = map_dict

    def insert_path_to_geometry(self, template_data):
        """Inserts ``include <first_geometry_file>`` line on the 6th line of
        Serpent2 input file.

        Parameters
        ----------
        template_data : list
            List of strings parsed from user's template file.

        Returns
        -------
        template_data : list
            List of strings containing modified path to geometry
            in user's template file.

        """
        template_data.insert(5,  # Inserts on 6th line
                             'include \"' + str(self.geo_files[0]) + '\"\n')
        return template_data

    def read_dep_comp(self, read_at_end=False):
        """Reads the Serpent2 `*_dep.m` file and returns a dictionary with
        a `Materialflow` object for each burnable material.

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
        # Determine moment in depletion step to read data from
        if read_at_end:
            moment = 1
        else:
            moment = 0

        dep_file = os.path.join('%s_dep.m' % self.iter_inputfile)
        dep = serpent.parse_dep(dep_file, make_mats=False)
        self.days = dep['DAYS'][moment]
        # Read materials names from the file
        mat_name = []
        mats = {}
        for key in dep.keys():
            m = re.search('MAT_(.+?)_VOLUME', key)
            if m:
                mat_name.append(m.group(1))
        zai = list(map(int, dep['ZAI'][:-2]))  # zzaaam codes of isotopes

        for m in mat_name:
            volume = dep['MAT_' + m + '_VOLUME'][moment]
            nucvec = dict(zip(zai, dep['MAT_' + m + '_MDENS'][:, moment]))
            mats[m] = Materialflow(nucvec)
            mats[m].density = dep['MAT_' + m + '_MDENS'][-1, moment]
            mats[m].mass = mats[m].density * volume
            mats[m].vol = volume
            mats[m].burnup = dep['MAT_' + m + '_BURNUP'][moment]
        self.create_nuclide_name_map_zam_to_serpent()
        return mats

    def read_depcode_info(self):
        """Parses initial simulation info data from Serpent2 output and stores
        it in the `DepcodeSerpent` object's ``sim_info`` attributes.
        """
        res = serpent.parse_res(self.iter_inputfile + "_res.m")
        depcode_name, depcode_ver = res['VERSION'][0].decode('utf-8').split()
        self.sim_info['depcode_name'] = depcode_name
        self.sim_info['depcode_version'] = depcode_ver
        self.sim_info['title'] = res['TITLE'][0].decode('utf-8')
        self.sim_info['depcode_input_filename'] = \
            res['INPUT_FILE_NAME'][0].decode('utf-8')
        self.sim_info['depcode_working_dir'] = \
            res['WORKING_DIRECTORY'][0].decode('utf-8')
        self.sim_info['xs_data_path'] = \
            res['XS_DATA_FILE_PATH'][0].decode('utf-8')
        self.sim_info['OMP_threads'] = res['OMP_THREADS'][0]
        self.sim_info['MPI_tasks'] = res['MPI_TASKS'][0]
        self.sim_info['memory_optimization_mode'] = res['OPTIMIZATION_MODE'][0]
        self.sim_info['depletion_timestep'] = res['BURN_DAYS'][1][0]
        self.sim_info['depletion_timestep'] = res['BURN_DAYS'][1][0]

    def read_depcode_step_param(self):
        """Parses data from Serpent2 output for each step and stores it in
        `DepcodeSerpent` object's ``param`` attributes.
        """
        res = serpent.parse_res(self.iter_inputfile + "_res.m")
        self.param['keff_bds'] = res['IMP_KEFF'][0]
        self.param['keff_eds'] = res['IMP_KEFF'][1]
        self.param['breeding_ratio'] = res['CONVERSION_RATIO'][1]
        self.param['execution_time'] = res['RUNNING_TIME'][1]
        self.param['burn_days'] = res['BURN_DAYS'][1][0]
        self.param['power_level'] = res['TOT_POWER'][1][0]
        self.param['memory_usage'] = res['MEMSIZE'][0]
        b_l = int(.5 * len(res['FWD_ANA_BETA_ZERO'][1]))
        self.param['beta_eff'] = res['FWD_ANA_BETA_ZERO'][1].reshape((b_l, 2))
        self.param['delayed_neutrons_lambda'] = \
            res['FWD_ANA_LAMBDA'][1].reshape((b_l, 2))
        self.param['fission_mass_bds'] = res['INI_FMASS'][1]
        self.param['fission_mass_eds'] = res['TOT_FMASS'][1]

    def read_plaintext_file(self, file_path):
        """Reads the content of a plaintext file for use by other methods.

        Parameters
        ----------
        file_path : str
            Path to file.

        Returns
        -------
        file_data : list
            List of strings containing file lines.

        """
        template_data = []
        with open(file_path, 'r') as file:
            template_data = file.readlines()
        return template_data

    def replace_burnup_parameters(
        self,
        template_data,
        reactor,
            current_depstep_idx):
        """Adds or replaces the ``set power P dep daystep DEPSTEP`` line in
        the Serpent2 input file. This line defines depletion history and power
        levels with respect to the depletion step in the single run and
        activates depletion calculation mode.

        Parameters
        ----------
        template_data : list
            List of strings parsed from user template file.
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        current_depstep_idx : int
            Current depletion step.

        Returns
        -------
        template_data : list
            List of strings containing modified in this function template file.

        """

        line_idx = 8  # burnup setting line index by default
        current_depstep_power = reactor.power_levels[current_depstep_idx]
        if current_depstep_idx == 0:
            current_depstep = reactor.dep_step_length_cumulative[0]
        else:
            current_depstep = \
                reactor.dep_step_length_cumulative[current_depstep_idx] - \
                reactor.dep_step_length_cumulative[current_depstep_idx - 1]
        for line in template_data:
            if line.startswith('set    power   '):
                line_idx = template_data.index(line)
                del template_data[line_idx]

        template_data.insert(line_idx,  # Insert on 9th line
                             'set    power   %5.9E   dep daystep   %7.5E\n' %
                             (current_depstep_power,
                              current_depstep))
        return template_data

    def run_depcode(self, cores, nodes):
        """Runs Serpent2 as a subprocess with the given parameters.

        Parameters
        ----------
        cores: int
            Number of cores to use for Serpent2 run (`-omp` flag in Serpent2).
        nodes: int
            Number of nodes to use for Serpent2 run (`-mpi` flag in Serpent2).

        """

        if self.exec_path.startswith('/projects/sciteam/bahg/'):  # check if BW
            args = (
                'aprun',
                '-n',
                str(nodes),
                '-d', str(cores),
                self.exec_path,
                '-omp',
                str(cores),
                self.iter_inputfile)
        elif self.exec_path.startswith('/apps/exp_ctl/'):  # check if Falcon
            args = (
                'mpiexec',
                self.exec_path,
                self.iter_inputfile,
                '-omp',
                str(18))
        else:
            args = (self.exec_path, '-omp', str(cores), self.iter_inputfile)
        print('Running %s' % (self.codename))
        try:
            subprocess.check_output(
                args,
                cwd=os.path.split(self.template_inputfiles_path)[0],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print(error.output.decode("utf-8"))
            raise RuntimeError('\n %s RUN FAILED\n see error message above'
                               % (self.codename))
        print('Finished Serpent2 Run')

    def convert_nuclide_name_serpent_to_zam(self, nuc_code):
        """Checks Serpent2-specific meta stable-flag for zzaaam. For instance,
        47310 instead of 471101 for `Ag-110m1`. Metastable isotopes represented
        with `aaa` started with ``3``.

        Parameters
        ----------
        nuc_code : str
            Name of nuclide in Serpent2 form. For instance, `47310`.

        Returns
        -------
        nuc_zzaam : int
            Name of nuclide in `zzaaam` form (`471101`).

        """
        zz = pyname.znum(nuc_code)
        aa = pyname.anum(nuc_code)
        if aa > 300:
            if zz > 76:
                aa_new = aa - 100
            else:
                aa_new = aa - 200
            zzaaam = str(zz) + str(aa_new) + '1'
        else:
            zzaaam = nuc_code
        return int(zzaaam)

    def switch_to_next_geometry(self):
        """Inserts line with path to next Serpent geometry file at the
        beginning of the Serpent iteration input file.
        """
        geo_line_n = 5
        f = open(self.iter_inputfile, 'r')
        data = f.readlines()
        f.close()

        current_geo_file = data[geo_line_n].split('\"')[1]
        current_geo_idx = self.geo_files.index(current_geo_file)
        try:
            new_geo_file = self.geo_files[current_geo_idx + 1]
        except IndexError:
            print('No more geometry files available \
                  and the system went subcritical \n\n')
            print('Aborting simulation')
            return
        new_data = [d.replace(current_geo_file, new_geo_file) for d in data]
        print('Switching to next geometry file: ', new_geo_file)

        f = open(self.iter_inputfile, 'w')
        f.writelines(new_data)
        f.close()

    def write_depcode_input(self, reactor, dep_step, restart):
        """Writes prepared data into the Serpent2 input file.

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

        if dep_step == 0 and not restart:
            data = self.read_plaintext_file(self.template_inputfiles_path)
            data = self.insert_path_to_geometry(data)
            data = self.change_sim_par(data)
            data = self.create_iter_matfile(data)
        else:
            data = self.read_plaintext_file(self.iter_inputfile)
        data = self.replace_burnup_parameters(data, reactor, dep_step)

        if data:
            out_file = open(self.iter_inputfile, 'w')
            out_file.writelines(data)
            out_file.close()

    def write_mat_file(self, dep_dict, dep_end_time):
        """Writes the iteration input file containing the burnable materials
        composition used in Serpent2 runs and updated after each depletion
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

        matf = open(self.iter_matfile, 'w')
        matf.write('%% Material compositions (after %f days)\n\n'
                   % dep_end_time)
        for key, value in dep_dict.items():
            matf.write('mat  %s  %5.9E burn 1 fix %3s %4i vol %7.5E\n' %
                       (key,
                        -dep_dict[key].density,
                        '09c',
                        dep_dict[key].temp,
                        dep_dict[key].vol))
            for nuc_code, wt_frac in dep_dict[key].comp.items():
                # Transforms iso name from zas to zzaaam and then to SERPENT
                iso_name_serpent = pyname.zzaaam(nuc_code)
                matf.write('           %9s  %7.14E\n' %
                           (self.iso_map[iso_name_serpent],
                            -wt_frac))
        matf.close()
