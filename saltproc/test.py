import os
from depcode import Depcode
from simulation import Simulation
import tables as tb

input_path = os.path.dirname(os.path.abspath(__file__))
# input_file = os.path.join(input_path, 'data/saltproc_tap')
# template_file = os.path.join(input_path, 'data/tap')
input_file = os.path.join(input_path, 'data/saltproc_tap')
template_file = os.path.join(input_path, 'data/tap')
iter_matfile = os.path.join(input_path, 'data/saltproc_mat')
db_file = os.path.join(input_path, 'data/db_saltproc.h5')
compression_prop = tb.Filters(complevel=9, complib='blosc', fletcher32=True)
# executable path of Serpent
exec_path = '/home/andrei2/serpent/serpent2/src_2131/sss2'
# Number of cores and nodes to use in cluster
cores = 4
steps = 3
# Monte Carlo method parameters
neutron_pop = 150
active_cycles = 100
inactive_cycles = 20
# Define materials (should read from input file)


if __name__ == "__main__":
    print('Initiating Saltproc:\n'
          # '\tRestart = ' + str(restart) + '\n'
          # '\tNodes = ' + str(nodes) + '\n'
          '\tCores = ' + str(cores) + '\n'
          # '\tSteps = ' + str(steps) + '\n'
          # '\tBlue Waters = ' + str(bw) + '\n'
          '\tSerpent Path = ' + exec_path + '\n'
          '\tTemplate File Path = ' + template_file + '\n'
          '\tInput File Path = ' + input_file + '\n'
          # '\tMaterial File Path = ' + mat_file + '\n'
          # '\tOutput DB File Path = ' + db_file + '\n'
          )

    serpent = Depcode(codename='SERPENT',
                      exec_path=exec_path,
                      template_fname=template_file,
                      input_fname=input_file,
                      output_fname='NONE',
                      iter_matfile=iter_matfile,
                      npop=neutron_pop,
                      active_cycles=active_cycles,
                      inactive_cycles=inactive_cycles)
    simulation = Simulation(sim_name='Super test',
                            sim_depcode=serpent,
                            core_number=cores,
                            h5_file=db_file,
                            compression=compression_prop,
                            iter_matfile=iter_matfile,
                            timesteps=steps)
    # print('End of RUN')
    # run.read_depcode_template()
    # Read templates for Depletion code, extract fuel composition in iter_mat
    # file, create input file for further loop calculations
    # serpent.write_depcode_input(template_file, input_file)
    # Run first iteration of depletion simulation
    # serpent.run_depcode(cores)
    # print(serpent.iter_matfile)
    simulation.runsim()
