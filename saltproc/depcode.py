import subprocess
import os
import shutil
from re import compile
from pyne import nucname as pyname
from collections import OrderedDict


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
            self.depl_dict = OrderedDict()
            self.depl_dict_n = OrderedDict()

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

    def read_bumat(self, input_file, moment):
        """ Reads depletion code output *.bumatx file and store it in two dict:
            depl_dict (nuclide codes are keys) and depl_dict_n (nuclide nuclide
            names are keys).
        """
        bu_format = compile(r'\s+Material compositions\s+\(([0-9E\.\+-]+) '
                            r'MWd/kgU\s+/\s+([0-9E\.\+-]+)')

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
                vol = float(z[4])
                self.depl_dict[mat_name] = {
                    'density': density,
                    'volume': vol,
                    'nuclides': OrderedDict({}),
                }
                self.depl_dict_n[mat_name] = {
                    'density': density,
                    'volume': vol,
                    'nuclides': OrderedDict({}),
                }
            else:
                nuc_code, adens = z[:2]
                nuc_name = self.get_nuc_name(nuc_code)
                self.depl_dict[mat_name]['nuclides'][nuc_code] = float(adens)
                # print ('Material %5s, nuclide name %8s, atomic density %5e'
                #        % (mat_name, nuc_name, float(adens)))
                self.depl_dict_n[mat_name]['nuclides'][nuc_name] = float(adens)
        # for i in range(len(nuc_name)):
        #      print (nuc_name[i]+'\r')
        # print (self.depl_dict['tit']['nuclides'])
        # nuclide_names = self.depl_dict_n['fuel']['nuclides'].keys()
        # print(nuclide_names)
        # print (self.depl_dict['fuel']['nuclides']['94239.09c'])
        # print (self.depl_dict.keys())
        # print (self.depl_dict['fuel']['volume'])
        # print (self.depl_dict['fuel']['density'])
        # print (self.depl_dict_n['fuel']['volume'])
        # print (self.depl_dict_n['fuel']['density'])
        # print (self.depl_dict['tit']['volume'])
        # print (self.burnup, self.days)
        # for x, y in self.depl_dict['tit']['nuclides'].items():
        #    print ('Nuclide name %8s and atomic density %5e' % (x, y))
        print (self.depl_dict_n)
        # print (len(self.depl_dict['tit']['nuclides'].values()))

    def get_nuc_name(self, nuc_code):
        """ Get nuclide name human readable notation. The chemical symbol(one
             or two characters), dash, and the atomic weight. Lastly if the
             nuclide metastable, the letter m is concatenated with number of
             excited state. Example 'Am-242m1'.
        """
        if '.' in nuc_code:
            nuc_code_id = pyname.mcnp_to_id(nuc_code.split('.')[0])
            zz = pyname.znum(nuc_code_id)
            aa = pyname.anum(nuc_code_id)
            aa_str = str(aa)
            if aa > 300:
                if zz > 76:
                    aa_str = str(aa-100)+'m1'
                else:
                    aa_str = str(aa-200)+'m1'
            nuc_name = pyname.zz_name[zz] + '-' + aa_str
        else:
            meta_flag = pyname.snum(nuc_code)
            if meta_flag:
                nuc_name = pyname.serpent(nuc_code)+str(pyname.snum(nuc_code))
            else:
                nuc_name = pyname.serpent(nuc_code)
        return nuc_name
