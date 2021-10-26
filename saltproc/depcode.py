from saltproc import Materialflow
import subprocess
import os
import shutil
import re
from pyne import nucname as pyname
from pyne import serpent
from abc import ABC, abstractmethod

# I borrowed this handy doc function from the OpenMC folks.
# See https://docs.openmc.org/en/stable/_modules/openmc/deplete/abc.html#Integrator
# yardasol -- 09.07.2022


def add_params(cls):
    cls.__doc__ += cls._params
    return cls


@add_params
class Depcode(ABC):
    r"""Class contains information about input, output, geometry, and template
    file for running depletion simulation code. Also contains neutrons
    population, active and inactive cycle. Contains methods to read template
    and output, write new input for the depletion code.
    """

    _params = r"""
    Parameters
    ----------
    codename : str
        Name of depletion code.
    exec_path : str
        Path to depletion code executable.
    template_fname : str
        Path to user input file for depletion code.
    input_fname : str
        Name of input file for depletion code rerunning.
    iter_matfile : str
        Name of iterative, rewritable material file for depletion code
        rerunning. This file is being modified during simulation.
    geo_file : str or list
        Path to file that contains the reactor geometry.
        List of `str` if reactivity control by
        switching geometry is `On` or just `str` otherwise.
    npop : int
        Size of neutron population per cycle for Monte Carlo.
    active_cycles : int
        Number of active cycles.
    inactive_cycles : int
        Number of inactive cycles.
    """

    def __init__(self,
                 codename,
                 exec_path,
                 template_fname,
                 input_fname,
                 iter_matfile,
                 geo_file=None,
                 npop=50,
                 active_cycles=20,
                 inactive_cycles=20):
        """Initializes the Depcode object.
        """
        self.codename = codename
        self.exec_path = exec_path
        self.template_fname = template_fname
        self.input_fname = input_fname
        self.iter_matfile = iter_matfile
        self.geo_file = geo_file
        self.npop = npop
        self.active_cycles = active_cycles
        self.inactive_cycles = inactive_cycles
        self.param = {}
        self.sim_info = {}

    @abstractmethod
    def read_dep_comp(self, dep_file, moment):
        """Reads the depleted material data from the depcode simulation
        and returns a dictionary with a `Materialflow` object for each
        burnable material.

        Parameters
        ----------
        dep_file : str
            Path to file containing results of depletion simulation
        moment : int
            The moment in the depletion step to read the data. `0`
            refers to the beginning of the depletion step, `1`
            refers to the end of the depeltion step.

        Returns
        -------
        mats : dict
            Dictionary that contains `Materialflow` objects.
            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.
        """

    @abstractmethod
    def run_depcode(self, cores, nodes):
        """Runs depletion code as subprocess with the given parameters.

        Parameters
        ----------
        cores : int
            Number of cores to use for depletion code run.
        nodes : int
            Number of nodes to use for depletion code run. 
        """

    @abstractmethod
    def write_depcode_input(self, temp, inp, reactor, dts, researt):
        """ Writes prepared data into depletion code input file(s).

        Parameters
        ----------
        temp : str
            Path to user template file for depletion code
        inp : str
            Path to input file for depletion code rerunning
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        dts : int
            Current depletion time step.
        restart : bool
            Is the current simulation restarted?
        """

    @abstractmethod
    def write_mat_file(self, dep_dict, mat_file, cumulative_time_at_eds):
        """Writes the iteration input file containing burnable materials
        composition used in depletion runs and updated after each depletion
        step.
        Parameters
        ----------
        mats : dict
            Dictionary that contains `Materialflow` objects.
            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.
        mat_file : str
            Path to file containing burnable materials composition.
        cumulative_time_at_eds : float
            Current time at the end of the depletion step (d).
        """


# @add_params
# class DepcodeOpenMC(Depcode):
#    r"""Class contains information about input, output, geometry, and
#    template file for running OpenMC depletion simulation
#    """
#    self.codename="OpenMC"


@add_params
class DepcodeSerpent(Depcode):
    r"""Class contains information about input, output, geometry, and
    template file for running Serpent2 depletion simulation
    """
    # self.codename="Serpent"

    def change_sim_par(self, data):
        """Finds simulation parameters (neutron population, cycles) in input
        file and change those to parameters from SaltProc input.

        Parameters
        ----------
        data : list
            List of strings parsed from user template file.

        Returns
        -------
        list
            List of strings containing modified user template file with new
            simulation parameters.

        """
        if self.npop and self.active_cycles and self.inactive_cycles:
            sim_param = [s for s in data if s.startswith("set pop")]
            if len(sim_param) > 1:
                print('ERROR: Template file %s contains multiple lines with '
                      'simulation parameters:\n'
                      % (self.template_fname), sim_param)
                return
            elif len(sim_param) < 1:
                print('ERROR: Template file %s does not contain line with '
                      'simulation parameters.' % (self.template_fname))
                return
            args = 'set pop %i %i %i\n' % (self.npop, self.active_cycles,
                                           self.inactive_cycles)
        return [s.replace(sim_param[0], args) for s in data]

    def create_iter_matfile(self, data):
        """Finds ``include`` line with path to material file, copies content of
        this file to iteration material file, changes path in ``include`` line
        to newly created iteration material file.

        Parameters
        ----------
        data : list
            List of strings parsed from user template file.

        Returns
        -------
        list
            List of strings containing modified user template file.

        """
        data_dir = os.path.dirname(self.template_fname)
        include_str = [s for s in data if s.startswith("include ")]
        if not include_str:
            print('ERROR: Template file %s has no <include "material_file">'
                  ' statements ' % (self.template_fname))
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
                      % (self.template_fname))
                return
        # Create data directory
        try:
            os.mkdir(os.path.dirname(self.iter_matfile))
        except FileExistsError:
            pass
        # Create file with path for SaltProc rewritable iterative material file
        shutil.copy2(abs_src_matfile, self.iter_matfile)
        return [s.replace(src_file, self.iter_matfile) for s in data]

    def get_nuc_name(self, nuc_code):
        """Returns nuclide name in human-readable notation: chemical symbol
        (one or two characters), dash, and the atomic weight. Lastly, if the
        nuclide is in metastable state, the letter `m` is concatenated with
        number of excited state. For example, `Am-242m1`.

        Parameters
        ----------
        nuc_code : str
            Name of nuclide in Serpent form. For instance, `Am-242m`.

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
                    aa_str = str(aa-100)+'m1'
                    aa = aa-100
                else:
                    aa_str = str(aa-200)+'m1'
                    aa = aa-200
                nuc_zzaaam = str(zz)+str(aa)+'1'
            elif aa == 0:
                aa_str = 'nat'
            nuc_name = pyname.zz_name[zz] + aa_str
        else:
            meta_flag = pyname.snum(nuc_code)
            if meta_flag:
                nuc_name = pyname.name(nuc_code)[:-1] + 'm'+str(meta_flag)
            else:
                nuc_name = pyname.name(nuc_code)
        nuc_zzaaam = self.sss_meta_zzz(pyname.zzaaam(nuc_code))
        return nuc_name, nuc_zzaaam

    def get_tra_or_dec(self, input_file):
        """Returns the isotopes map to transform isotope `zzaaam` code to
        Serpent. Uses Serpent `*.out` file with list of all isotopes in
        simulation.

        Parameters
        -----------
        input_file: str
            Serpent input file name and path.

        Returns
        --------
        dict
            Contains mapping for isotopes names from `zzaaam` to Serpent name
            imported from Serpent ouput file:

            ``key``
                The key is nuclide name in `zzaaam` format. For example,
                `922350` or `982510`.
            ``value``
                Serpent-oriented name. For instance, 92235.09c for transport
                isotope or 982510 for decay only isotope).

        """
        map_dict = {}
        # Construct path to the *.out File
        out_file = os.path.join('%s.out' % input_file)
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

    def insert_path_to_geometry(self, data):
        """Inserts ``include <first_geometry_file>`` line on th 6th line of
        Serpent input file.

        Parameters
        ----------
        data : list
            List of strings parsed from user template file.

        Returns
        -------
        list
            List of strings containing modified in this function template file.

        """
        data.insert(5,  # Inserts on 6th line
                    'include \"' + str(self.geo_file[0]) + '\"\n')
        return data

    def read_dep_comp(self, input_file, moment):
        """Reads the Serpent `*_dep.m` file and returns dictionary with
        `Materialflow` object for each burnable material.

        Parameters
        ----------
        input_file : str
            Path to Serpent input file.
        moment : int
            Indicates at which moment in the depletion step read the data. `0`
            refers the beginning, `1` refers the end of depletion step.

        Returns
        -------
        mats : dict
            Dictionary that contains `Materialflow` objects.

            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.

        """
        dep_file = os.path.join('%s_dep.m' % input_file)
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
            volume = dep['MAT_'+m+'_VOLUME'][moment]
            nucvec = dict(zip(zai, dep['MAT_'+m+'_MDENS'][:, moment]))
            mats[m] = Materialflow(nucvec)
            mats[m].density = dep['MAT_'+m+'_MDENS'][-1, moment]
            mats[m].mass = mats[m].density*volume
            mats[m].vol = volume
            mats[m].burnup = dep['MAT_'+m+'_BURNUP'][moment]
        self.get_tra_or_dec(self.input_fname)
        return mats

    def read_depcode_info(self):
        """Parses initial simulation info data from Serpent output and stores
        it in `Depcode` object ``sim_info`` attributes.
        """
        res = serpent.parse_res(self.input_fname + "_res.m")
        self.sim_info['serpent_version'] = \
            res['VERSION'][0].decode('utf-8')
        self.sim_info['title'] = res['TITLE'][0].decode('utf-8')
        self.sim_info['serpent_input_filename'] = \
            res['INPUT_FILE_NAME'][0].decode('utf-8')
        self.sim_info['serpent_working_dir'] = \
            res['WORKING_DIRECTORY'][0].decode('utf-8')
        self.sim_info['xs_data_path'] = \
            res['XS_DATA_FILE_PATH'][0].decode('utf-8')
        self.sim_info['OMP_threads'] = res['OMP_THREADS'][0]
        self.sim_info['MPI_tasks'] = res['MPI_TASKS'][0]
        self.sim_info['memory_optimization_mode'] = res['OPTIMIZATION_MODE'][0]
        self.sim_info['depletion_timestep'] = res['BURN_DAYS'][1][0]
        self.sim_info['depletion_timestep'] = res['BURN_DAYS'][1][0]

    def read_depcode_step_param(self):
        """Parses data from Serpent output for each step and stores it in
        `Depcode` object ``param`` attributes.
        """
        res = serpent.parse_res(self.input_fname + "_res.m")
        self.param['keff_bds'] = res['IMP_KEFF'][0]
        self.param['keff_eds'] = res['IMP_KEFF'][1]
        self.param['breeding_ratio'] = res['CONVERSION_RATIO'][1]
        self.param['execution_time'] = res['RUNNING_TIME'][1]
        self.param['burn_days'] = res['BURN_DAYS'][1][0]
        self.param['power_level'] = res['TOT_POWER'][1][0]
        self.param['memory_usage'] = res['MEMSIZE'][0]
        b_l = int(.5*len(res['FWD_ANA_BETA_ZERO'][1]))
        self.param['beta_eff'] = res['FWD_ANA_BETA_ZERO'][1].reshape((b_l, 2))
        self.param['delayed_neutrons_lambda'] = \
            res['FWD_ANA_LAMBDA'][1].reshape((b_l, 2))
        self.param['fission_mass_bds'] = res['INI_FMASS'][1]
        self.param['fission_mass_eds'] = res['TOT_FMASS'][1]

    def read_depcode_template(self, template_fname):
        """Reads prepared template (input) file for depeletion code for further
        changes in the file to prepare input file for multiple runs.

        Parameters
        ----------
        template_fname: str
            Path to user template file for depletion code.

        Returns
        -------
        list
            List of strings containing user template file.

         """
        file = open(template_fname, 'r')
        str_list = file.readlines()
        return str_list

    def replace_burnup_parameters(self, data, reactor, current_depstep_idx):
        """Adds or replaces ``set power P dep daystep DEPSTEP`` line in Serpent
        input file. The line defines depletion history and power levels with
        depletion step in the single run and activates depletion calculation
        mode.

        Parameters
        ----------
        data : list
            List of strings parsed from user template file.
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        current_depstep_idx : int
            Current depletion step.

        Returns
        -------
        list
            List of strings containing modified in this function template file.

        """

        line_idx = 8  # burnup setting line index by default
        current_depstep_power = reactor.power_levels[current_depstep_idx]
        if current_depstep_idx == 0:
            current_depstep = reactor.depl_hist[0]
        else:
            current_depstep = reactor.depl_hist[current_depstep_idx] - \
                reactor.depl_hist[current_depstep_idx-1]
        for line in data:
            if line.startswith('set    power   '):
                line_idx = data.index(line)
                del data[line_idx]

        data.insert(line_idx,  # Insert on 9th line
                    'set    power   %5.9E   dep daystep   %7.5E\n' %
                    (current_depstep_power,
                     current_depstep))
        return data

    def run_depcode(self, cores, nodes):
        """Runs depletion code as subprocess with the given parameters.

        Parameters
        ----------
        cores: int
            Number of cores to use for Serpent run (`-omp` flag in Serpent).
        nodes: int
            Number of nodes to use for Serpent run (`-mpi` flag in Serpent).

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
                self.input_fname)
        elif self.exec_path.startswith('/apps/exp_ctl/'):  # check if Falcon
            args = (
                'mpiexec',
                self.exec_path,
                self.input_fname,
                '-omp',
                str(18))
        else:
            args = (self.exec_path, '-omp', str(cores), self.input_fname)
        print('Running %s' % (self.codename))
        try:
            subprocess.check_output(
                args,
                cwd=os.path.split(self.template_fname)[0],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print(error.output.decode("utf-8"))
            raise RuntimeError('\n %s RUN FAILED\n see error message above'
                               % (self.codename))
        print('Finished Serpent Run')

    def sss_meta_zzz(self, nuc_code):
        """Checks Serpent-specific meta stable-flag for zzaaam. For instance,
        47310 instead of 471101 for `Ag-110m1`. Metastable isotopes represented
        with `aaa` started with ``3``.

        Parameters
        ----------
        nuc_code : str
            Name of nuclide in Serpent form. For instance, `47310`.

        Returns
        -------
        int
            Name of nuclide in `zzaaam` form (`471101`).

        """
        zz = pyname.znum(nuc_code)
        aa = pyname.anum(nuc_code)
        if aa > 300:
            if zz > 76:
                aa_new = aa-100
            else:
                aa_new = aa-200
            zzaaam = str(zz)+str(aa_new)+'1'
        else:
            zzaaam = nuc_code
        return int(zzaaam)

    def write_depcode_input(self, temp_file, inp_file, reactor, dts, restart):
        """Writes prepared data into the depletion code input file.

        Parameters
        ----------
        template_file : str
            Path to user template file for depletion code..
        input_file : str
            Path to input file for depletion code rerunning.
        reactor : Reactor
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        dts : int
            Current depletion time step.
        restart : bool
            Is the current simulation restarted?

        Returns
        -------
        type
            Description of returned object.

        """

        if dts == 0 and not restart:
            data = self.read_depcode_template(temp_file)
            data = self.insert_path_to_geometry(data)
            data = self.change_sim_par(data)
            data = self.create_iter_matfile(data)
        else:
            data = self.read_depcode_template(inp_file)
        data = self.replace_burnup_parameters(data, reactor, dts)

        if data:
            out_file = open(inp_file, 'w')
            out_file.writelines(data)
            out_file.close()

    def write_mat_file(self, dep_dict, mat_file, cumulative_time_at_eds):
        """Writes the iteration input file containing burnable materials
        composition used in depletion runs and updated after each depletion
        step.

        Parameters
        ----------
        mats : dict
            Dictionary that contains `Materialflow` objects.

            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.
        mat_file : str
            Path to file containing burnable materials composition.
        cumulative_time_at_eds : float
            Current time at the end of the depletion step (d).

        """

        matf = open(mat_file, 'w')
        matf.write('%% Material compositions (after %f days)\n\n'
                   % cumulative_time_at_eds)
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
