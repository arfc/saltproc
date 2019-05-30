from saltproc import *
# from saltproc import Depcode
# from saltproc import Simulation
# from depcode import Depcode
# from simulation import Simulation
# from materialflow import Materialflow
import os
import tables as tb

input_path = os.path.dirname(os.path.abspath(__file__)) + '/../saltproc/'
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
steps = 1
# Monte Carlo method parameters
neutron_pop = 50
active_cycles = 20
inactive_cycles = 10
# Define materials (should read from input file)


def reprocessing(mat):
    """ Applies reprocessing scheme to selected material
    """
    # Create Process object based on input_file
    heat_exchanger = Process(mass_flowrate=10,
                             capacity=100.0,
                             volume=1.0,
                             inflow=mat,
                             # outflow,
                             # waste_stream = 'bucket',
                             efficiency={'Xe135': 0.95},
                             )
    outflow = heat_exchanger.do_removals(mat, {'Xe': 0.})
    # for key, value in mat.items():
    #     print (key, value, outflow[key])
    print(mat[541350000], outflow[541350000])
    print(mat[541340000], outflow[541340000])
    print(mat[541360000], outflow[541360000])

def main():
    """ Inititialize main run
    """
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

    # Run sequence
    # simulation.runsim_no_reproc()
    # Start sequence
    for dts in range(steps):
        print ("\nStep #%i has been started" % (dts+1))
        if dts == 0:  # First step
            """serpent.write_depcode_input(template_file, input_file)
            serpent.run_depcode(cores)
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dts)"""
            mats = serpent.read_dep_comp(input_file, 1)  # 0)
            # simulation.store_mat_data(mats, dts, 'before_reproc')  # store init
            # Reprocessing here
            reprocessing(mats['fuel'])
        # Finish of First step
        # Main sequence
        else:
            serpent.run_depcode(cores)
        """mats = serpent.read_dep_comp(input_file, 1)
        simulation.store_mat_data(mats, dts, 'before_reproc')
        simulation.store_run_step_info()
        serpent.write_mat_file(mats, iter_matfile, dts)"""


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

    main()
    print("\nSimulation succeeded.\n")
