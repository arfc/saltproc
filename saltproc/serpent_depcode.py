from pathlib import Path
import subprocess
import os
import shutil
import re

from pyne import nucname as pyname
from pyne import serpent

from saltproc import Materialflow
from saltproc.abc import Depcode

class SerpentDepcode(Depcode):
    """Class contains information about input, output, geometry, and
    template files for running Serpent2 depletion simulations.
    Also contains neutrons population, active, and inactive cycles.
    Contains methods to read template and output files,
    write new input files for Serpent2.

    Attributes
    -----------
    neutronics_parameters : dict of str to type
        Holds Serpent2 depletion step neutronics parameters. Parameter names are
        keys and parameter values are values.
    step_metadata : dict of str to type
        Holds Serpent2 depletion step metadata. Metadata labels are keys
        and metadata values are values.
    iter_inputfile : str
        Path to Serpent2 input file for Serpent2 rerunning.
    iter_matfile : str
        Path to iterative, rewritable material file for Serpent2
        rerunning. This file is modified during the simulation.

    """

    def __init__(self,
                 exec_path="sss2",
                 template_input_file_path="reactor.serpent",
                 geo_files=None,
                 npop=50,
                 active_cycles=20,
                 inactive_cycles=20):
        """Initializes the SerpentDepcode object.

           Parameters
           ----------
           exec_path : str
               Path to Serpent2 executable.
           template_input_file_path : str
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
                         template_input_file_path,
                         geo_files=geo_files,
                         npop=npop,
                         active_cycles=active_cycles,
                         inactive_cycles=inactive_cycles)
        self.iter_inputfile = './serpent_iter_input.serpent'
        self.iter_matfile = './serpent_iter_mat.ini'

    def apply_neutron_settings(self, file_lines):
        """Apply neutron settings (no. of neutrons per cycle, no. of active and
        inactive cycles) from the SaltProc input file to the runtime Serpent2
        input file.

        Parameters
        ----------
        file_lines : list of str
            Serpent2 runtime input file.

        Returns
        -------
        file_lines : list of str
            Serpent2 runtime input file with updated neutron settings.

        """
        if self.npop and self.active_cycles and self.inactive_cycles:
            neutron_settings = \
                [line for line in file_lines if line.startswith("set pop")]
            if len(neutron_settings) > 1:
                raise IOError('Template file '
                              f'{self.template_input_file_path} contains '
                              'multuple lines with neutron settings')
            elif len(neutron_settings) < 1:
                raise IOError('Template file '
                              f'{self.template_input_file_path} does not '
                              'contain neutron settings.')
            args = 'set pop %i %i %i\n' % (self.npop, self.active_cycles,
                                           self.inactive_cycles)
        return [line.replace(neutron_settings[0], args) for line in file_lines]

    def create_runtime_matfile(self, file_lines):
        """Creates the runtime material file tracking burnable materials
        ans inserts the path to this file in the Serpent2 runtime input file

        Parameters
        ----------
        file_lines : list of str
            Serpent2 runtime input file.

        Returns
        -------
        file_lines : list of str
            Serpent2 runtime input file with updated material file path.

        """
        runtime_dir = Path(self.template_input_file_path).parents[0]
        include_str = [line for line in file_lines if line.startswith("include ")]
        if not include_str:
            raise IOError('Template file '
                          f'{self.template_input_file_path} has no <include '
                          '"material_file"> statements')
        src_file = include_str[0].split()[1][1:-1]
        if not Path(src_file).is_absolute():
            abs_src_matfile = (runtime_dir / src_file)
        else:
            abs_src_matfile = Path(src_file)
            with open(abs_src_matfile) as f:
                if 'mat ' not in f.read():
                    raise IOError('Template file '
                                  f'{self.template_input_file_path} includes '
                                  'no file with materials description')
        # Create data directory
        Path.mkdir(Path(self.iter_matfile).parents[0], exist_ok=True)

        # Create file with path for SaltProc rewritable iterative material file
        shutil.copy2(abs_src_matfile, self.iter_matfile)
        return [line.replace(src_file, self.iter_matfile) for line in file_lines]

    def convert_nuclide_code_to_name(self, nuc_code):
        """Converts Serpent2 nuclide code to symbolic nuclide name.
        If nuclide is in a metastable state, the nuclide name is concatenated
        with the letter `m` and the state index.

        Parameters
        ----------
        nuc_code : str
            Nuclide code in Serpent2 format (`47310.09c`)

        Returns
        -------
        nuc_name : str
            Symbolic nuclide name (`Am242m1`).

        """

        if '.' in str(nuc_code):
            nuc_code = pyname.zzzaaa_to_id(int(nuc_code.split('.')[0]))
            zz = pyname.znum(nuc_code)
            aa = pyname.anum(nuc_code)
            aa_str = str(aa)
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

        return nuc_name

    def map_nuclide_code_zam_to_serpent(self):
        """Creates a dictionary mapping nuclide codes in `zzaaam` format
        to Serpent2's nuclide code format.

        Returns
        -------
        nuc_code_map : dict of str to str
            Maps `zzaaam` nuclide codes to Serpent2
            nuclide codes.

            ``key``
                Nuclide code in `zzaaam` format. For example,
                `922350` or `982510`.
            ``value``
                Nuclide code in Serpent2 format. For instance, 92235.09c for a
                nuclide with cross section data or 982510 for a decay-only nuclide.

        """
        nuc_code_map = {}
        # Construct path to the *.out File
        out_file = os.path.join('%s.out' % self.iter_inputfile)
        with open(out_file, 'r') as f:
            file_lines = f.read().split('\n')
            # Stop-line
            end = ' --- Table  2: Reaction and decay data: '
            for line in file_lines:
                if not line:
                    continue
                if end in line:
                    break
                if 'c  TRA' in line or 'c  DEC' in line:
                    line = line.split()
                    nuc_code = line[2]
                    if '.' in str(nuc_code):
                        nuc_code = pyname.zzzaaa_to_id(int(nuc_code.split('.')[0]))

                    zzaaam = \
                        self.convert_nuclide_code_to_zam(pyname.zzaaam(nuc_code))

                    nuc_code_map.update({zzaaam: line[2]})
        return nuc_code_map

    def insert_path_to_geometry(self, lines):
        """Inserts ``include <first_geometry_file>`` line on the 6th line of
        Serpent2 input file.

        Parameters
        ----------
        lines : list of str
            Serpent2 runtime input file.

        Returns
        -------
        lines : list of str
            Serpent 2 runtime input file containing modified path to geometry

        """
        lines.insert(5,  # Inserts on 6th line
                             'include \"' + str(self.geo_files[0]) + '\"\n')
        return lines

    def read_depleted_materials(self, read_at_end=False):
        """Reads depleted materials from Serpent2's `*_dep.m`
        file and returns a dictionary containing them.

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
        # Determine moment in depletion step to read data from
        if read_at_end:
            moment = 1
        else:
            moment = 0

        results_file = os.path.join('%s_dep.m' % self.iter_inputfile)
        results = serpent.parse_dep(results_file, make_mats=False)
        self.days = results['DAYS'][moment]

        # Get material names
        mat_names = []
        depleted_materials = {}
        for key in results.keys():
            name_match = re.search('MAT_(.+?)_VOLUME', key)
            if name_match:
                mat_names.append(name_match.group(1))
        zai = list(map(int, results['ZAI'][:-2]))  # zzaaam codes of isotopes

        for name in mat_names:
            volume = results[f'MAT_{name}_VOLUME'][moment]
            nucvec = dict(zip(zai, results[f'MAT_{name}_MDENS'][:, moment]))
            depleted_materials[name] = Materialflow(nucvec)
            depleted_materials[name].density = results[f'MAT_{name}_MDENS'][-1, moment]
            depleted_materials[name].mass = depleted_materials[name].density * volume
            depleted_materials[name].vol = volume
            depleted_materials[name].burnup = results[f'MAT_{name}_BURNUP'][moment]
        return depleted_materials

    def read_step_metadata(self):
        """Reads Serpent2 depletion step metadata and stores it in the
        :class:`SerpentDepcode` object's :attr:`step_metadata` attribute.
        """
        res = serpent.parse_res(self.iter_inputfile + "_res.m")
        depcode_name, depcode_ver = res['VERSION'][0].decode('utf-8').split()
        self.step_metadata['depcode_name'] = depcode_name
        self.step_metadata['depcode_version'] = depcode_ver
        self.step_metadata['title'] = res['TITLE'][0].decode('utf-8')
        self.step_metadata['depcode_input_filename'] = \
            res['INPUT_FILE_NAME'][0].decode('utf-8')
        self.step_metadata['depcode_working_dir'] = \
            res['WORKING_DIRECTORY'][0].decode('utf-8')
        self.step_metadata['xs_data_path'] = \
            res['XS_DATA_FILE_PATH'][0].decode('utf-8')
        self.step_metadata['OMP_threads'] = res['OMP_THREADS'][0]
        self.step_metadata['MPI_tasks'] = res['MPI_TASKS'][0]
        self.step_metadata['memory_optimization_mode'] = res['OPTIMIZATION_MODE'][0]
        self.step_metadata['depletion_timestep'] = res['BURN_DAYS'][1][0]
        self.step_metadata['execution_time'] = res['RUNNING_TIME'][1]
        self.step_metadata['memory_usage'] = res['MEMSIZE'][0]


    def read_neutronics_parameters(self):
        """Reads Serpent2 depletion step neutronics parameters and stores them
        in :class:`SerpentDepcode` object's :attr:`neutronics_parameters`
        attribute.
        """
        res = serpent.parse_res(self.iter_inputfile + "_res.m")
        self.neutronics_parameters['keff_bds'] = res['IMP_KEFF'][0]
        self.neutronics_parameters['keff_eds'] = res['IMP_KEFF'][1]
        self.neutronics_parameters['breeding_ratio'] = \
            res['CONVERSION_RATIO'][1]
        self.neutronics_parameters['burn_days'] = res['BURN_DAYS'][1][0]
        self.neutronics_parameters['power_level'] = res['TOT_POWER'][1][0]
        b_l = int(.5 * len(res['FWD_ANA_BETA_ZERO'][1]))
        self.neutronics_parameters['beta_eff'] = \
            res['FWD_ANA_BETA_ZERO'][1].reshape((b_l, 2))
        self.neutronics_parameters['delayed_neutrons_lambda'] = \
            res['FWD_ANA_LAMBDA'][1].reshape((b_l, 2))
        self.neutronics_parameters['fission_mass_bds'] = \
            res['INI_FMASS'][1]
        self.neutronics_parameters['fission_mass_eds'] = \
            res['TOT_FMASS'][1]

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

    def set_power_load(self,
                       file_lines,
                       reactor,
                       current_depstep_idx):
        """Add power load attributes in a :class:`Reactor` object to the
        ``set power P dep daystep DEPSTEP`` line in the Serpent2  runtime input
        file.

        Parameters
        ----------
        file_lines : list of str
            Serpent2 runtime input file.
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        current_depstep_idx : int
            Current depletion step.

        Returns
        -------
        file_lines : list of str
            Serpent2 runtime input file with power load specification.

        """

        line_idx = 8  # burnup setting line index by default
        current_depstep_power = reactor.power_levels[current_depstep_idx]
        if current_depstep_idx == 0:
            current_depstep = reactor.dep_step_length_cumulative[0]
        else:
            current_depstep = \
                reactor.dep_step_length_cumulative[current_depstep_idx] - \
                reactor.dep_step_length_cumulative[current_depstep_idx - 1]
        for line in file_lines:
            if line.startswith('set    power   '):
                line_idx = file_lines.index(line)
                del file_lines[line_idx]

        file_lines.insert(line_idx,  # Insert on 9th line
                          'set    power   %5.9E   dep daystep   %7.5E\n' %
                          (current_depstep_power, current_depstep))
        return file_lines

    def run_depletion_step(self, cores, nodes):
        """Runs a depletion step in Serpent2 as a subprocess with the given
        parameters.

        Parameters
        ----------
        cores: int
            Number of cores to use for Serpent2 run (`-omp` flag in Serpent2).
        nodes: int
            Number of nodes to use for Serpent2 run (`-mpi` flag in Serpent2).

        """

        args = (self.exec_path, '-omp', str(cores), self.iter_inputfile)
        print('Running %s' % (self.codename))
        try:
            subprocess.check_output(
                args,
                cwd=os.path.split(self.template_input_file_path)[0],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print(error.output.decode("utf-8"))
            raise RuntimeError('\n %s RUN FAILED\n see error message above'
                               % (self.codename))
        print('Finished Serpent2 Run')

    def convert_nuclide_code_to_zam(self, nuc_code):
        """Converts nuclide code from Serpent2 format to zam format.
        Checks Serpent2-specific meta stable-flag for zzaaam. For instance,
        47310 instead of 471101 for `Ag-110m1`. Metastable isotopes represented
        with `aaa` started with ``3``.

        Parameters
        ----------
        nuc_code : int
            Nuclide code in Serpent2 format (`47310`).

        Returns
        -------
        nuc_zzaam : int
            Nuclide code in in `zzaaam` form (`471101`).

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
        with open(self.iter_inputfile, 'r') as f:
            lines = f.readlines()

        current_geo_file = lines[geo_line_n].split('\"')[1]
        current_geo_idx = self.geo_files.index(current_geo_file)
        try:
            new_geo_file = self.geo_files[current_geo_idx + 1]
        except IndexError:
            print('No more geometry files available \
                  and the system went subcritical \n\n')
            print('Aborting simulation')

        new_lines = \
            [line.replace(current_geo_file, new_geo_file) for line in lines]
        print('Switching to next geometry file: ', new_geo_file)

        with open(self.iter_inputfile, 'w') as f:
            f.writelines(new_lines)

    def write_depletion_step_input(self, reactor, dep_step, restart):
        """Write Serpent2 input file for running depletion step

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
            lines = self.read_plaintext_file(self.template_input_file_path)
            lines = self.insert_path_to_geometry(lines)
            lines = self.apply_neutron_settings(lines)
            lines = self.create_runtime_matfile(lines)
        else:
            lines = self.read_plaintext_file(self.iter_inputfile)
        lines = self.set_power_load(lines, reactor, dep_step)

        with open(self.iter_inputfile, 'w') as out_file
            out_file.writelines(lines)

    def update_depletable_materials(self, mats, dep_end_time):
        """Update material file with reprocessed material compositions.

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

        with open(self.iter_matfile, 'w') as f:
            f.write('%% Material compositions (after %f days)\n\n'
                    % dep_end_time)
            nuc_code_map = self.map_nuclide_code_zam_to_serpent()
            for name, mat in mats.items():
                f.write('mat  %s  %5.9E burn 1 fix %3s %4i vol %7.5E\n' %
                        (name,
                         -mat.density,
                         '09c',
                         mat.temp,
                         mat.vol))
                for nuc_code, mass_fraction in mat.comp.items():
                    zam_code = pyname.zzaaam(nuc_code)
                    f.write('           %9s  %7.14E\n' %
                            (nuc_code_map[zam_code],
                             -mass_fraction))
