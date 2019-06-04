from saltproc import Depcode
from saltproc import Simulation
from saltproc import Process
# from depcode import Depcode
# from simulation import Simulation
# from materialflow import Materialflow
import os
import copy
import tables as tb
import json


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
neutron_pop = 100
active_cycles = 20
inactive_cycles = 5
# Define materials (should read from input file)
core_massflow_rate = 9.92e+6  # g/s


def read_processes_from_input():
    processes = {}
    with open('input.json') as f:
        j = json.load(f)
        # print(j['extraction_processes'])
        for obj_name, obj_data in j['extraction_processes'].items():
            processes[obj_name] = Process(**obj_data)
        # print(processes)
        # print('\nProcess objects attributes:')
        # print("Sparger efficiency ", processes['sparger'].efficiency)
        # print("Ni filter efficiency", processes['nickel_filter'].efficiency)
        # print(processes['sparger'].mass_flowrate)
        # print(processes['entrainment_separator'].mass_flowrate)
        return processes


def reprocessing(mat):
    """ Applies reprocessing scheme to selected material
    """
    waste = {}
    outflow = {}
    prcs = read_processes_from_input()
    p = ['heat_exchanger', 'sparger', 'entrainment_separator', 'nickel_filter', 'liquid_me_extraction']
    # 1 via Heat exchanger
    outflow[p[1]], waste[p[1]] = prcs[p[1]].rem_elements(mat)
    # 2 via sparger
    # outflow[p[1]], waste[p[1]] = prcs[p[1]].rem_elements(outflow[p[0]])
    # 3 via entrainment entrainment
    # outflow[p[2]], waste[p[2]] = prcs[p[2]].rem_elements(outflow[p[1]])
    # Split to two paralell flows A and B
    # A, 50% of mass flowrate
    # inflowA = 0.5*copy.deepcopy(outflow[p[2]])
    # outflowA1, waste[p[3]] = prcs[p[3]].rem_elements(inflowA)
    # B, 10% of mass flowrate
    # inflowB = 0.1*copy.deepcopy(outflow[p[2]])
    # outflowB1, waste[p[4]] = prcs[p[4]].rem_elements(inflowB)
    # C. rest of mass flow
    # outflowC = (1.-0.5-0.1)*copy.deepcopy(outflow[p[2]])
    # Feed here
    # Merge flows
    reprocessing_outflow = mat
    # reprocessing_outflow = outflowA1 + outflowB1 + outflowC
    """print('Waste stream from heat_exchanger', waste['heat_exchanger'])
    print('Waste stream from sparger', waste['sparger'])
    print('Waste stream from separator', waste['entrainment_separator'])
    print('Waste stream from Ni filter', waste['nickel_filter'])
    print('Waste stream from Molten salt/liquid metal extraction', waste['liquid_me_extraction'])
    print('\nMass balance %f g = %f + %f + %f + %f + %f' % (mat.mass,
                                                            reprocessing_outflow.mass,
                                                            waste[p[1]].mass,
                                                            waste[p[2]].mass,
                                                            waste[p[3]].mass,
                                                            waste[p[4]].mass))"""
    # total_out = reprocessing_outflow.mass
    # for i in range(len(p)):
#         total_out += waste[p[i]].mass
    # print("Balance %f = %f" % (mat.mass, total_out))
    # print(mat.__class__)
    # print(reprocessing_outflow.__class__)
    # return reprocessing_outflow, waste


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
    mats_after_repr = {}
    for dts in range(steps):
        print ("\nStep #%i has been started" % (dts+1))
        if dts == 0:  # First step
            # serpent.write_depcode_input(template_file, input_file)
            # serpent.run_depcode(cores)
            # Read general simulation data which never changes
            # simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dts
            mats = serpent.read_dep_comp(input_file, 1)  # 0)
            # simulation.store_mat_data(mats, dts, 'before_reproc')  # store init
            # Reprocessing here
            name_reproc_mat = 'fuel'
            # mats_after_repr[name_reproc_mat], waste =
            reprocessing(mats[name_reproc_mat])
            # print(mats_after_repr)
            # print(mats_after_repr['fuel'].mass)
            # print(mats_after_repr['fuel'].vol)
            # print(mats_after_repr['fuel'].temp)
            # print(waste)
        # Finish of First step
        # Main sequence
#        else:
            # serpent.run_depcode(cores)
        # mats = serpent.read_dep_comp(input_file, 1)
        # simulation.store_mat_data(mats, dts, 'before_reproc')
        # simulation.store_run_step_info()
        # serpent.write_mat_file(mats, iter_matfile, dts)


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
