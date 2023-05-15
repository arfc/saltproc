from pathlib import Path
import os
import shutil
import re

import serpentTools
import openmc
import openmc.data
from math import floor

from saltproc import Materialflow
from saltproc.depcode import Depcode

class SerpentDepcode(Depcode):
    """Interface for running depletion steps in Serpent, as well as obtaining
    depletion step results.

    Parameters
    ----------
    output_path : str
        Path to results storage directory.
    exec_path : str
        Path to Serpent2 executable.
    template_input_file_path : str
        Path to user input file for Serpent2
    geo_file_paths : str or list
        Path to file that contains the reactor geometry.
        List of `str` if reactivity control by
        switching geometry is `On` or just `str` otherwise.
    zaid_convention : str
        ZAID naming convention for nuclide codes.

        'serpent' - The third digit in ZA for nuclides in isomeric states
        is 3 (e.g. 47310 for for Ag-110m).

        'mcnp' - ZA = Z*1000 + A + (300 + 100*m). where m is the mth
        isomeric state (e.g. 47510 for Ag-110m)

        'nndc' - Identical to 'mcnp', except Am242m1 is 95242 and Am242
        is 95642

    Attributes
    ----------
    neutronics_parameters : dict of str to type
        Holds Serpent2 depletion step neutronics parameters. Parameter names are
        keys and parameter values are values.
    step_metadata : dict of str to type
        Holds Serpent2 depletion step metadata. Metadata labels are keys
        and metadata values are values.
    runtime_inputfile : str
        Path to Serpent2 input file used to run depletion step. Contains neutron
        settings and non-burnable materials.
    runtime_matfile : str
        Path to Serpent2 material file containing burnable materials used to
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
                 zaid_convention):
        """Initialize a SerpentDepcode object.

        """
        super().__init__("serpent",
                         output_path,
                         exec_path,
                         template_input_file_path,
                         geo_file_paths)
        self.runtime_inputfile = \
                         str((output_path / 'runtime_input.serpent').resolve())
        self.runtime_matfile = str((output_path / 'runtime_mat.ini').resolve())
        self.zaid_convention = zaid_convention
        self._OUTPUTFILE_NAMES = ('runtime_input.serpent_res.m', 'runtime_input.serpent_dep.m',
                                 'runtime_input.serpent.seed', 'runtime_input.serpent.out',
                                 'runtime_input.serpent.dep')
        self._INPUTFILE_NAMES = ('runtime_mat.ini', 'runtime_input.serpent')

    def get_neutron_settings(self, file_lines):
        """Get neutron settings (no. of neutrons per cycle, no. of active and
        inactive cycles) from the Serpent2 input file

        Parameters
        ----------
        file_lines : list of str
            Serpent2 runtime input file.

        """
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
        _, _, npop, active_cycles, inactive_cycles = neutron_settings[0].split()
        self.npop = int(npop)
        self.active_cycles = int(active_cycles)
        self.inactive_cycles = int(inactive_cycles)

    def create_runtime_matfile(self, file_lines):
        """Creates the runtime material file tracking burnable materials
        and inserts the path to this file in the Serpent2 runtime input file

        Parameters
        ----------
        file_lines : list of str
            Serpent2 runtime input file.

        Returns
        -------
        file_lines : list of str
            Serpent2 runtime input file with updated material file path.

        """
        burnable_materials_path, absolute_path = self._get_burnable_materials_file(file_lines)

        # Create data directory
        Path.mkdir(Path(self.runtime_matfile).parents[0], exist_ok=True)

        # Get material cards
        flines = self.read_plaintext_file(absolute_path)
        self._get_burnable_material_card_data(flines)

         # Create file with path for SaltProc rewritable iterative material file
        shutil.copy2(absolute_path, self.runtime_matfile)
        return [line.replace(burnable_materials_path, self.runtime_matfile) for line in file_lines]

    def _get_burnable_materials_file(self, file_lines):
        runtime_dir = Path(self.template_input_file_path).parents[0]
        include_card = [line for line in file_lines if line.startswith("include ")]
        if not include_card:
            raise IOError('Template file '
                          f'{self.template_input_file_path} has no <include '
                          '"material_file"> statements')
        burnable_materials_path = include_card[0].split()[1][1:-1]
        if not Path(burnable_materials_path).is_absolute():
            absolute_path = (runtime_dir / burnable_materials_path)
        else:
            absolute_path = Path(burnable_materials_path)
        with open(absolute_path) as f:
            if 'mat ' not in f.read():
                raise IOError('Template file '
                              f'{self.template_input_file_path} includes '
                              'no file with materials description')
        return burnable_materials_path, absolute_path.resolve()

    def _get_burnable_material_card_data(self, file_lines):
        # Get data for matfile
        mat_cards = \
            [line.split() for line in file_lines if line.startswith("mat ")]

        for card in mat_cards:
            if 'fix' not in card:
                raise IOError(f'"mat" card for burnable material "{card[1]}"'
                              ' does not have a "fix" option. Burnable materials'
                              ' in SaltProc must include the "fix" option. See'
                              ' the serpent wiki for more information:'
                              ' https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#mat')
        # Get volume indices
        card_volume_idx = [(card.index('vol') + 1) for card in mat_cards]
        mat_names = [card[1] for card in mat_cards]
        mat_data = zip(mat_cards, card_volume_idx)#, mat_extensions)
        self._burnable_material_card_data = dict(zip(mat_names, mat_data))

    def nuclide_code_to_name(self, nuc_code):
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
            Symbolic nuclide name (`Am242_m1`).

        """

        if '.' in str(nuc_code):
            nuc_code = int(nuc_code.split('.')[0])
            if self.zaid_convention == 'nndc' and nuc_code in (95242, 95642):
               if nuc_code == 95242:
                  nuc_code = 95642
               else:
                  nuc_code = 95242
            Z, a, m = self._nuclide_code_to_zam(nuc_code)
        else:
            Z, a, m = self._decay_code_to_zam(nuc_code)

        nucname = openmc.data.gnds_name(Z, a, m=m)
        if m != 0:
            nucname = nucname[:-3] + f'_m{m}'
        return nucname

    def _decay_code_to_zam(self, nuc_code):
        m = int(str(nuc_code)[-1])
        nuc_code = int(str(nuc_code)[:-1])
        Z = floor(nuc_code * 1e-3)
        a = nuc_code % 1000
        return Z, a, m

    def _nuclide_code_to_zam(self, nuc_code):
        if '.' in str(nuc_code):
            nuc_code = int(nuc_code.split('.')[0])

        Z = floor(nuc_code * 1e-3)
        a = nuc_code % 1000
        m = 0
        if self.zaid_convention == 'serpent':
            if a > 300:
                m = 1
                if Z > 76:
                    a = a - 100
                else:
                    a = a - 200
        else:
            # Assumes only m=1 metastable states
            if a > 400:
                a -= 400
                m = 1
        return Z, a, m

    def name_to_nuclide_code(self, nucname):
        Z, a, m = openmc.data.zam(nucname)
        nuc_code = self._zam_to_nuclide_code(Z, a, m)
        return nuc_code

    def _zam_to_nuclide_code(self, Z, a, m):
        nuc_code = Z * 1000
        if m != 0:
            if self.zaid_convention == 'serpent':
                nuc_code += int(((a / 100) - 3) * 100)
            else:
                nuc_code += 300 + 100 * m
                if self.zaid_convention == 'nndc' and nuc_code in (95242, 95642):
                   if nuc_code == 95242:
                      nuc_code = 95642
                   else:
                      nuc_code = 95242
        return nuc_code


    def map_nuclide_name_to_serpent_name(self):
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
        out_file = os.path.join('%s.out' % self.runtime_inputfile)
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
                    nuc_name = self.nuclide_code_to_name(nuc_code)
                    nuc_code_map.update({nuc_name: nuc_code})
        return nuc_code_map

    def resolve_include_paths(self, lines):
        """Resolves relative paths in runtime input file into
        absolute paths.

        Parameters
        ----------
        lines : list of str
            Serpent2 runtime input file.

        Returns
        -------
            lines : list of str
                Serpent 2 runtime input file containing modified `include` paths

        """
        for idx, line in enumerate(lines):
            if line.startswith('include'):
                split_line = line.split(' ')
                include_path = split_line[1].split('\"')[1]
                include_path = \
                    Path(self.template_input_file_path).parents[0] / include_path
                include_path = include_path.resolve()
                line = f'include \"{str(include_path)}\"\n'
                lines[idx] = line

        return lines

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
                             'include \"' + str(self.geo_file_paths[0]) + '\"\n')
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

        openmc.reset_auto_ids()
        results_file = os.path.join('%s_dep.m' % self.runtime_inputfile)
        results = serpentTools.read(results_file)
        self.days = results.days[moment]

        # Get material names
        mat_names = []
        depleted_materials = {}
        for material_name, material in results.materials.items():
            if material_name != 'total':
                nuclide_names = list(map(self.nuclide_code_to_name, material.zai[:-2]))
                comp = dict(zip(nuclide_names, material.mdens[:-2, moment]))
                volume = material.volume[moment]
                density = material.mdens[-1, moment]
                depleted_materials[material_name] = Materialflow(comp=comp,
                                                                 comp_is_density=True,
                                                                 density=density,
                                                                 volume=volume,
                                                                 burnup=results.burnup[moment])
        return depleted_materials

    def read_step_metadata(self):
        """Reads Serpent2 depletion step metadata and stores it in the
        :class:`SerpentDepcode` object's :attr:`step_metadata` attribute.
        """
        res = serpentTools.read(self.runtime_inputfile + "_res.m")
        depcode_name, depcode_ver = res.metadata['version'].split()
        self.step_metadata['depcode_name'] = depcode_name
        self.step_metadata['depcode_version'] = depcode_ver
        self.step_metadata['title'] = res.metadata['title']
        self.step_metadata['depcode_input_filename'] = \
            res.metadata['inputFileName']
        self.step_metadata['depcode_working_dir'] = \
            res.metadata['workingDirectory']
        self.step_metadata['xs_data_path'] = \
            res.metadata['xsDataFilePath']
        self.step_metadata['OMP_threads'] = res.metadata['ompThreads']
        self.step_metadata['MPI_tasks'] = res.metadata['mpiTasks']
        self.step_metadata['memory_optimization_mode'] = res.metadata['optimizationMode']
        self.step_metadata['depletion_timestep'] = res.resdata['burnDays'][1][0]
        self.step_metadata['execution_time'] = res.resdata['runningTime'][1]
        self.step_metadata['memory_usage'] = res.resdata['memsize'][0]


    def read_neutronics_parameters(self):
        """Reads Serpent2 depletion step neutronics parameters and stores them
        in :class:`SerpentDepcode` object's :attr:`neutronics_parameters`
        attribute.
        """
        res = serpentTools.read(self.runtime_inputfile + "_res.m")
        self.neutronics_parameters['keff_bds'] = res.resdata['impKeff'][0]
        self.neutronics_parameters['keff_eds'] = res.resdata['impKeff'][1]
        self.neutronics_parameters['breeding_ratio_bds'] = \
            res.resdata['conversionRatio'][0]
        self.neutronics_parameters['breeding_ratio_eds'] = \
            res.resdata['conversionRatio'][1]
        self.neutronics_parameters['burn_days'] = res.resdata['burnDays'][1][0]
        self.neutronics_parameters['power_level'] = res.resdata['totPower'][1][0]
        b_l = int(.5 * len(res['fwdAnaBetaZero'][1]))
        self.neutronics_parameters['beta_eff_bds'] = \
            res.resdata['fwdAnaBetaZero'][0].reshape((b_l, 2))
        self.neutronics_parameters['beta_eff_eds'] = \
            res.resdata['fwdAnaBetaZero'][1].reshape((b_l, 2))
        self.neutronics_parameters['delayed_neutrons_lambda_bds'] = \
            res.resdata['fwdAnaLambda'][0].reshape((b_l, 2))
        self.neutronics_parameters['delayed_neutrons_lambda_eds'] = \
            res.resdata['fwdAnaLambda'][1].reshape((b_l, 2))
        self.neutronics_parameters['fission_mass_bds'] = \
            res.resdata['iniFmass'][1]
        self.neutronics_parameters['fission_mass_eds'] = \
            res.resdata['totFmass'][1]

    def set_power_load(self,
                       file_lines,
                       reactor,
                       step_idx):
        """Set the power for the current depletion step

        Parameters
        ----------
        file_lines : list of str
            Serpent2 runtime input file.
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        step_idx : int
            Current depletion step.

        Returns
        -------
        file_lines : list of str
            Serpent2 runtime input file with power load specification.

        """

        line_idx = 8  # burnup setting line index by default
        current_power = reactor.power_levels[step_idx]

        step_length = reactor.depletion_timesteps[step_idx]

        for line in file_lines:
            if line.startswith('set    power   '):
                line_idx = file_lines.index(line)
                del file_lines[line_idx]

        if reactor.timestep_units == 'MWd/kg':
            step_type = 'bu'
        else:
            step_type = 'day'

        step_type += 'step'

        file_lines.insert(line_idx,
                          f'set    power   %5.9E   dep %s   %7.5E\n' %
                          (current_power, step_type, step_length))
        return file_lines

    def run_depletion_step(self, mpi_args=None, threads=None):
        """Runs a depletion step in Serpent2 as a subprocess.

i       Parameters
        ----------
        mpi_args : list of str
            Arguments for running simulations on supercomputers using
            ``mpiexec`` or similar programs.
        threads : int
            Threads to use for shared-memory parallelism

        """

        args = [self.exec_path]

        if mpi_args is not None:
            args = mpi_args + args

        if threads is not None:
            args = args + ['-omp', str(threads)]

        args = args + [self.runtime_inputfile]

        super().run_depletion_step(mpi_args, args)

    def switch_to_next_geometry(self):
        """Inserts line with path to next Serpent geometry file at the
        beginning of the Serpent iteration input file.
        """
        geo_line_n = 5
        with open(self.runtime_inputfile, 'r') as f:
            lines = f.readlines()

        current_geo_file = lines[geo_line_n].split('\"')[1]
        current_geo_idx = self.geo_file_paths.index(current_geo_file)
        try:
            new_geo_file = self.geo_file_paths[current_geo_idx + 1]
        except IndexError:
            print('No more geometry files available \
                  and the system went subcritical \n\n')
            print('Aborting simulation')

        new_lines = \
            [line.replace(current_geo_file, new_geo_file) for line in lines]
        print('Switching to next geometry file: ', new_geo_file)

        with open(self.runtime_inputfile, 'w') as f:
            f.writelines(new_lines)

    def write_runtime_input(self, reactor, dep_step, restart):
        """Write Serpent2 runtime input file for running depletion step

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
            lines = self.resolve_include_paths(lines)
            lines = self.insert_path_to_geometry(lines)
            lines = self.create_runtime_matfile(lines)
            self.get_neutron_settings(lines)
        else:
            lines = self.read_plaintext_file(self.runtime_inputfile)
        lines = self.set_power_load(lines, reactor, dep_step)

        with open(self.runtime_inputfile, 'w') as out_file:
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

        with open(self.runtime_matfile, 'w') as f:
            f.write('%% Material compositions (after %f days)\n\n'
                    % dep_end_time)
            nuc_code_map = self.map_nuclide_name_to_serpent_name()
            if not(hasattr(self, '_burnable_material_card_data')):
                lines = self.read_plaintext_file(self.template_input_file_path)
                _, abs_src_matfile = self._get_burnable_materials_file(lines)
                file_lines = self.read_plaintext_file(abs_src_matfile)
                self._get_burnable_material_card_data(file_lines)
            for name, mat in mats.items():
                mat_card, card_volume_idx = self._burnable_material_card_data[name]
                mat_card[2] = str(-mat.density)
                mat_card[card_volume_idx] = "%7.5E" % mat.volume
                f.write(" ".join(mat_card))
                f.write("\n")
                for nuc, mass_fraction in mat.comp.items():
                    f.write('           %9s  %7.14E\n' %
                            (nuc_code_map[nuc],
                             -mass_fraction))
