import subprocess
import os


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
            npop: int
                size of neutron population for Monte-Carlo code
            active_cycles: int
                number of active cycles
            inactive_cycles: int
                number of inactive cycles
            """
            # initialize all object attributes
            self.codename = codename
            self.exec_path = exec_path
            self.template_fname = template_fname
            self.input_fname = input_fname
            self.output_fname = output_fname
            self.npop = npop
            self.active_cycles = active_cycles
            self.inactive_cycles = inactive_cycles

    def run_depcode(self, cores):
        """ Runs depletion code as subprocess with the given parameters"""
        print('Running %s' % self.codename)
        args = (self.exec_path, '-omp', str(cores), self.input_fname)
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
        """ Check simulation parameters (neutron population, cycles) and changes
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

    def write_depcode_input(self, template_file, input_file):
        """ Write prepared data into depletion code input file """
        if os.path.exists(input_file):
            os.remove(input_file)
        data = self.read_depcode_template(template_file)
        changed_data = self.change_sim_par(data)
        if changed_data:
            out_file = open(input_file, 'w')
            out_file.writelines(changed_data)
            out_file.close()
