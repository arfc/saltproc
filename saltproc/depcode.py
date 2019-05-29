from saltproc import Materialflow as matflow
import subprocess
import os
import copy
import shutil
from re import compile
import re
from scipy import constants as const
from collections import OrderedDict
from pyne import nucname as pyname
from pyne import serpent
from pyne import data as pydata
from pyne.material import Material as pymat


class Depcode:
    """ Class contains information about input, output, geometry, and template
    file for running depletion simulation code. Also contains information about
     neutrons population, active and inactive cycle, etc. Read template and
      output, write new input for the depletion code.
    """

    def __init__(
                self,
                codename,
                exec_path,
                template_fname,
                input_fname,
                output_fname,
                iter_matfile,
                npop=None,
                active_cycles=None,
                inactive_cycles=None):
            """ Initializes the class

            Parameters:
            -----------
            codename: string
                name of the code for depletion
            exec_path: string
                path to depletion code executable
            template_fname: string
                name of user input file for depletion code with geometry and
                 initial composition
            input_fname: string
                name of input file for depletion code rerunning
            output_fname: string
                name of output file for depletion code rerunning
            iter_matfile: string
                name of iterative rewritable material file for depletion code
                 rerunning
            npop: int
                size of neutron population for Monte-Carlo code
            active_cycles: int
                number of active cycles
            inactive_cycles: int
                number of inactive cycles
            depl_dict: dict
                key: material name
                value: density, volume, dict: 'nuclides'
                key: nuclide code in Serpent format (95342.09c or 952421)
                value: atomic density
            depl_dict_n: dict
                key: material name
                value: density, volume, dict: 'nuclides'
                key: nuclide name in human readable format (Am-242m1)
                value: atomic density
            """
            # initialize all object attributes
            self.codename = codename
            self.exec_path = exec_path
            self.template_fname = template_fname
            self.input_fname = input_fname
            self.output_fname = output_fname
            self.iter_matfile = iter_matfile
            self.npop = npop
            self.active_cycles = active_cycles
            self.inactive_cycles = inactive_cycles
    sim_info = {
                "serpent_version": [],
                "title": [],
                "serpent_input_filename": [],
                "serpent_working_dir": [],
                "xs_data_path": [],
                "OMP_threads": [],
                "MPI_tasks": [],
                "memory_optimization_mode": []
                }
    param = {
            "keff_bds": [],
            "keff_eds": [],
            "breeding_ratio": [],
            "execution_time": [],
            "memory_usage": [],
            "beta_eff": [],
            "delayed_neutrons_lambda": [],
            "fission_mass_bds": [],
            "fission_mass_eds": []
            }

    def run_depcode(self, cores):
        """ Runs depletion code as subprocess with the given parameters"""
        args = (self.exec_path, '-omp', str(cores), self.input_fname)
        print('Running %s' % (self.codename))
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError as error:
            print(error.output)
            raise ValueError('\n %s RUN FAILED\n' % (self.codename))
        print('Finished Serpent Run')

    def read_depcode_template(self, template_fname):
        """ Reads prepared template (input) file for Depeletion code for
         further changes in the file to prepare input file for multiple runs"""
        file = open(template_fname, 'r')
        str_list = file.readlines()
        return str_list

    def change_sim_par(self, data):
        """ Check simulation parameters (neutron population, cycles) and change
         to parameters from SaltProc input """
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
        """ Check <include> with material file, copy in iteration material file,
         and change name of file in <include> """
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
        # Create file with path for SaltProc rewritable iterative material file
        shutil.copy2(abs_src_matfile, self.iter_matfile)
        return [s.replace(src_file, self.iter_matfile) for s in data]

    def write_depcode_input(self, template_file, input_file):
        """ Write prepared data into depletion code input file """
        if os.path.exists(input_file):
            os.remove(input_file)
        data = self.read_depcode_template(template_file)
        data = self.change_sim_par(data)
        data = self.create_iter_matfile(data)
        if data:
            out_file = open(input_file, 'w')
            out_file.writelines(data)
            out_file.close()

    def read_bumat(self, input_file, munits, moment):
        """ Reads depletion code output *.bumatx file and store it in two dict:
            depl_dict (nuclide codes are keys) and depl_dict_n (nuclide nuclide
            names are keys).
        """
        bu_format = compile(r'\s+Material compositions\s+\(([0-9E\.\+-]+) '
                            r'MWd/kgU\s+/\s+([0-9E\.\+-]+)')

        depl_dict = OrderedDict()
        depl_dict_h = OrderedDict()
        nucvec = {}
        bu_match = None
        mat_name = None
        bumat_fname = os.path.join(input_file + ".bumat" + str(moment))
        file = open(bumat_fname, 'r')
        str_list = file.read().split('\n')
        for line in str_list:
            line = line.strip()
            if not line:
                continue
            if bu_match is None:
                bu_match = bu_format.search(line)
                if bu_match is not None:
                    self.burnup, self.days = [
                        float(z) for z in bu_match.groups()]
                    continue
            elif line[0] == '%':
                continue
            z = line.split()
            if z[0] == 'mat':
                mat_name = z[1]
                density = float(z[2])
                if 'fix' in z:
                    vol = float(z[7])
                else:
                    vol = float(z[4])
                depl_dict[mat_name] = {
                    'density': density,
                    'volume': vol,
                    'lib_temp': None,
                    'temperature': None,
                    'nuclides': OrderedDict({}),
                }
                depl_dict_h[mat_name] = copy.deepcopy(depl_dict[mat_name])
            else:
                nuc_code, adens = z[:2]
                if '.' in nuc_code and depl_dict[mat_name]['lib_temp'] is None:
                    lib_code = nuc_code.split('.')[1]
                    temp_val = 100 * int(lib_code.replace('c', ''))
                    depl_dict[mat_name]['lib_temp'] = lib_code
                    depl_dict_h[mat_name]['lib_temp'] = lib_code
                    depl_dict[mat_name]['temperature'] = temp_val
                    depl_dict_h[mat_name]['temperature'] = temp_val
                nuc_name, nuc_zzaaam, atomic_mass = self.get_nuc_name(nuc_code)
                depl_dict[mat_name]['nuclides'][nuc_code] = float(adens)
                # Make dictionary with isotopes names and mass to store in hdf5
                # determine multiplier for mass units convertion
                if munits is "g":
                    mul_m = 1.
                elif munits is "kg":
                    mul_m = 1.E-3
                elif munits is "t" or "ton" or "tonne" or "MT":
                    mul_m = 1.E-6
                else:
                    raise ValueError(
                          'Mass units does not supported or does not defined')
                mass = vol * (1e+24*mul_m*float(adens)*atomic_mass) / const.N_A
                depl_dict_h[mat_name]['nuclides'][nuc_name] = [mass]
                # print ('%5s, %8s, zzaaam %7s, aensity %5e, at mass %5f'
                #        % (mat_name, nuc_name, nuc_zzaaam, float(adens),
                #           atomic_mass))
                nucvec[nuc_zzaaam] = float(adens)
        mat_name = pymat()
        mat_name.density = 3.6
        mat_name.mass = 200.E+6
        mat_name.metadata = str(mat_name)
        mat_name.atoms_per_molecule = -1.0
        mat_name.from_atom_frac(nucvec)
        return depl_dict, depl_dict_h

    def read_dep_comp(self, input_file, moment):
        """ Reads the SERPENT _dep.m file and return mat_composition.
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
            mats[m] = matflow(nucvec)
            mats[m].density = dep['MAT_'+m+'_MDENS'][-1, moment]
            mats[m].mass = mats[m].density*volume
            mats[m].vol = volume
            mats[m].burnup = dep['MAT_'+m+'_BURNUP'][moment]
        # mat_name.atoms_per_molecule = -1.0
        # print (mats['fuel'])
        # print (mats['ctrlPois'].mass)
        # print (mats['ctrlPois']['O16'])
        # print (mats['ctrlPois']['Al27'])
        # print (mats['ctrlPois'])
        # for key, value in mats.items():
        #    print ("Object material:", key, "\n", value)
        # print (mat1.metadata)
        # mat1_composition = mat1.comp
        # print(mat1_composition[170370000])
        # print(mat1_composition[pyname.id('Cl37')])
        # Generate map for transforming iso name fprm zas to SERPENT
        self.get_tra_or_dec()
        return mats

    def write_mat_file(self, dep_dict, mat_file, step):
        """ Writes the input fuel composition input file block
        """
        matf = open(mat_file, 'w')
        matf.write('%% Material compositions (after %f days)\n\n'
                   % (self.days*(step+1)))
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

    def sss_meta_zzz(self, nuc_code):
        """ Check special SERPENT meta stable-flag for zzaaam (i.e. 47310 insead
            of 471101)
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

    def get_nuc_name(self, nuc_code):
        """ Get nuclide name human readable notation. The chemical symbol(one
             or two characters), dash, and the atomic weight. Lastly if the
             nuclide metastable, the letter m is concatenated with number of
             excited state. Example 'Am-242m1'.
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
            nuc_name = pyname.zz_name[zz] + '-' + aa_str
        else:
            meta_flag = pyname.snum(nuc_code)
            at_mass = pydata.atomic_mass(nuc_code)
            if meta_flag:
                nuc_name = pyname.name(nuc_code)+str(pyname.snum(nuc_code))
            else:
                nuc_name = pyname.name(nuc_code)
        nuc_zzaaam = self.sss_meta_zzz(pyname.zzaaam(nuc_code))
        at_mass = pydata.atomic_mass(pyname.id(nuc_zzaaam))
        # print ("Nuclide %s; zzaaam %i" % (nuc_name, nuc_zzaaam))
        return nuc_name, nuc_zzaaam, at_mass  # .encode('utf8')

    def read_depcode_info(self):
        """ Parses initial simulation info data from Serpent output
        """
        res = serpent.parse_res(self.input_fname + "_res.m")
        self.sim_info['serpent_version'].append(
                                res['VERSION'][0].decode('utf-8'))
        self.sim_info['title'].append(res['TITLE'][0].decode('utf-8'))
        self.sim_info['serpent_input_filename'].append(
                                res['INPUT_FILE_NAME'][0].decode('utf-8'))
        self.sim_info['serpent_working_dir'].append(
                                res['WORKING_DIRECTORY'][0].decode('utf-8'))
        self.sim_info['xs_data_path'].append(
                                res['XS_DATA_FILE_PATH'][0].decode('utf-8'))
        self.sim_info['OMP_threads'].append(res['OMP_THREADS'][0])
        self.sim_info['MPI_tasks'].append(res['MPI_TASKS'][0])
        self.sim_info['memory_optimization_mode'].append(
                                                res['OPTIMIZATION_MODE'][0])

    def read_depcode_step_param(self):
        """ Parses data from Serpent output for each step and stores it in dict
        """
        res = serpent.parse_res(self.input_fname + "_res.m")
        self.param['keff_bds'].append(res['IMP_KEFF'][0])
        self.param['keff_eds'].append(res['IMP_KEFF'][1])
        self.param['breeding_ratio'].append(res['CONVERSION_RATIO'][1])
        self.param['execution_time'].append(res['RUNNING_TIME'][1])
        self.param['memory_usage'].append(res['MEMSIZE'][0])
        self.param['beta_eff'].append(
                                res['FWD_ANA_BETA_ZERO'][1].reshape((9, 2)))
        self.param['delayed_neutrons_lambda'].append(
                                res['FWD_ANA_LAMBDA'][1].reshape((9, 2)))
        self.param['fission_mass_bds'].append(res['INI_FMASS'][1])
        self.param['fission_mass_eds'].append(res['TOT_FMASS'][1])

    def get_tra_or_dec(self):
        """ Returns the isotopes map to tranform isotope zzaaam code to SERPENT

        Parameters:
        -----------

        Returns:
        --------
        iso_map: dict
            contain mapping for isotopes names from zzaaam fprmat to SERPENT
            key: zzaaam name of specific isotope
            value: Serpent-oriented name (i.e. 92235.09c for transport isotope
                   or 982510 for decay only isotope)
        """
        map_dict = {}
        # Construct path to the *.out File
        out_file = os.path.join('%s.out' % self.input_fname)
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
                iname, zzaaam, imass = self.get_nuc_name(line[2])
                # print (zzaaam, line[2], iname, imass)
                map_dict.update({zzaaam: line[2]})
        self.iso_map = map_dict
