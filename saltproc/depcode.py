import subprocess
import os
import copy
import shutil
from re import compile
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
    keff = {
            "keff_BOC": [],
            "keff_EOC": [],
            "Breeding_ratio": [],
            "Execution_time": [],
            "Beta_eff": [],
            "Delayed_neutrons_lambda": [],
            "Fission_mass_BOC": [],
            "Fission_mass_EOC": [],
            "Burnup": []
            }

    def run_depcode(self, cores):
        """ Runs depletion code as subprocess with the given parameters"""
        print('Running %s' % self.codename)
        args = (self.exec_path, '-omp', str(cores), self.input_fname)
        print('Running %s' % (self.codename))
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError as error:
            print(error.output)
            raise ValueError('\n %s RUN FAILED\n' % self.codename)
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
                nucvec[nuc_zzaaam] = float(mass)
        fuel = pymat(nucvec, density=3.6)
        # print (fuel)
        fuel_at_perc = fuel.to_atom_dens()
        # print (fuel_at_perc)
        totm = 0
        for iso, value in fuel_at_perc.items():
            if abs(fuel_at_perc[iso]) > 0.0:
                totm += 1E-24*fuel_at_perc[iso]
                print("%5s, wt %7.12E" % (pyname.name(iso),
                                          1E-24*fuel_at_perc[iso]))
        print (totm)
        return depl_dict, depl_dict_h

    def write_mat_file(self, dep_dict, mat_file, step):
        """ Writes the input fuel composition input file block
        """
        matf = open(mat_file, 'w')
        matf.write('%% Material compositions (%f MWd/kgU / %f days)\n\n'
                   % (self.burnup*step, self.days*step))
        for key, value in dep_dict.items():
            matf.write('mat  %s  %7.14E fix %3s %4i burn 1 vol %7.5E\n' %
                       (key,
                        dep_dict[key]['density'],
                        dep_dict[key]['lib_temp'],
                        dep_dict[key]['temperature'],
                        dep_dict[key]['volume']))
            for nuc_code, adens in dep_dict[key]['nuclides'].items():
                matf.write('           %9s  %7.14E\n' %
                           (nuc_code,
                            adens))
        matf.close()

    def get_nuc_name(self, nuc_code):
        """ Get nuclide name human readable notation. The chemical symbol(one
             or two characters), dash, and the atomic weight. Lastly if the
             nuclide metastable, the letter m is concatenated with number of
             excited state. Example 'Am-242m1'.
        """
        if '.' in nuc_code:
            nuc_code = pyname.mcnp_to_id(nuc_code.split('.')[0])
            zz = pyname.znum(nuc_code)
            aa = pyname.anum(nuc_code)
            aa_str = str(aa)
            # at_mass = pydata.atomic_mass(nuc_code_id)
            if aa > 300:
                if zz > 76:
                    aa_str = str(aa-100)+'m1'
                    aa_new = aa-100
                else:
                    aa_str = str(aa-200)+'m1'
                    aa_new = aa-200
                nuc_zzaaam = str(zz)+str(aa_new)+'1'
            nuc_name = pyname.zz_name[zz] + '-' + aa_str
        else:
            meta_flag = pyname.snum(nuc_code)
            at_mass = pydata.atomic_mass(nuc_code)
            if meta_flag:
                nuc_name = pyname.serpent(nuc_code)+str(pyname.snum(nuc_code))
            else:
                nuc_name = pyname.serpent(nuc_code)
        nuc_zzaaam = pyname.zzaaam(nuc_code)
        at_mass = pydata.atomic_mass(pyname.id(nuc_zzaaam))
        # print ("Nuclide %s; atomic mass %f" % (nuc_name, at_mass))
        return nuc_name, nuc_zzaaam, at_mass  # .encode('utf8')

    def read_out(self):
        """ Parses data from Serpent output for each step and stores it in dict
        """
        res = serpent.parse_res(self.input_fname + "_res.m")
        self.keff['keff_BOC'].append(res['IMP_KEFF'][0])
        self.keff['keff_EOC'].append(res['IMP_KEFF'][1])
        self.keff['Breeding_ratio'].append(res['CONVERSION_RATIO'][1])
        self.keff['Execution_time'].append(res['TOT_CPU_TIME'][0] +
                                           res['TOT_CPU_TIME'][1])
        self.keff['Beta_eff'].append(res['BETA_EFF'][1, ::2])
        self.keff['Delayed_neutrons_lambda'].append(res['LAMBDA'][1, ::2])
        self.keff['Fission_mass_BOC'].append(res['INI_FMASS'][1])
        self.keff['Fission_mass_EOC'].append(res['TOT_FMASS'][1])
        self.keff['Burnup'].append(res['BURNUP'][1])
