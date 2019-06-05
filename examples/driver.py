from saltproc import Depcode
from saltproc import Simulation
from saltproc import Materialflow
from saltproc import Process
# from depcode import Depcode
# from simulation import Simulation
# from materialflow import Materialflow
import os
import copy
import tables as tb
import json


input_path = os.path.dirname(os.path.abspath(__file__)) + '/../saltproc/'
input_file = os.path.join(input_path, 'data/saltproc_tap')
template_file = os.path.join(input_path, 'data/tap')
iter_matfile = os.path.join(input_path, 'data/saltproc_mat')
db_file = os.path.join(input_path, 'data/db_saltproc.h5')
compression_prop = tb.Filters(complevel=9, complib='blosc', fletcher32=True)
# executable path of Serpent
exec_path = '/home/andrei2/serpent/serpent2/src_2131/sss2'
restart_flag = False
pc_type = 'pc'  # 'bw', 'falcon'
# Number of cores and nodes to use in cluster
cores = 4
steps = 3
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


def read_feeds_from_input():
    feeds = {}
    with open('input.json') as f:
        j = json.load(f)
        # print(j['feeds'])
        for obj_name, obj_data in j['feeds'].items():
            # print(obj_data)
            nucvec = obj_data['comp']
            feeds[obj_name] = Materialflow(nucvec)
            feeds[obj_name].mass = obj_data['mass']
            feeds[obj_name].density = obj_data['density']
            feeds[obj_name].vol = obj_data['volume']
        # print(feeds['leu'])
        # print(feeds['leu'].print_attr())
        return feeds


def reprocessing(mat):
    """ Applies reprocessing scheme to selected material

    Parameters:
    -----------
    mat: Materialflow object`
        Material data right after irradiation in the core/vesel
    Returns:
    --------
    out: Materialflow object
        Material data after performing all removals
    waste: dictionary
        key: process name
        value: Materialflow object containing waste streams data
    """
    waste = {}
    outflow = {}
    prcs = read_processes_from_input()
    p = ['heat_exchanger',
         'sparger',
         'entrainment_separator',
         'nickel_filter',
         'liquid_me_extraction']
    # 1 via Heat exchanger
    outflow[p[0]], waste[p[0]] = prcs[p[0]].rem_elements(mat)
    # 2 via sparger
    outflow[p[1]], waste[p[1]] = prcs[p[1]].rem_elements(outflow[p[0]])
    # 3 via entrainment entrainment
    outflow[p[2]], waste[p[2]] = prcs[p[2]].rem_elements(outflow[p[1]])
    # Split to two paralell flows A and B
    # A, 50% of mass flowrate
    inflowA = 0.5*outflow[p[2]]
    print("InflowA", inflowA.__class__, inflowA.mass, inflowA.density)
    outflow[p[3]], waste[p[3]] = prcs[p[3]].rem_elements(inflowA)
    # B, 10% of mass flowrate
    inflowB = 0.1*outflow[p[2]]
    outflow[p[4]], waste[p[4]] = prcs[p[4]].rem_elements(inflowB)
    # C. rest of mass flow
    outflowC = 0.4*outflow[p[2]]
    # Feed here
    # Merge out flows
    out = outflow[p[3]] + outflow[p[4]] + outflowC
    print('\nMass balance %f g = %f + %f + %f + %f + %f' % (mat.mass,
                                                            out.mass,
                                                            waste[p[1]].mass,
                                                            waste[p[2]].mass,
                                                            waste[p[3]].mass,
                                                            waste[p[4]].mass))
    print('\nMass balance', out.mass+waste[p[1]].mass+waste[p[2]].mass+waste[p[3]].mass+waste[p[4]].mass)
    print('Volume ', inflowA.vol, inflowB.vol, inflowA.vol+inflowB.vol)
    print('Mass flowrate ', inflowA.mass_flowrate, inflowB.mass_flowrate, out.mass_flowrate)
    print('Burnup ', inflowA.burnup, inflowB.burnup)
    print('\n\n')
    # print('\nInflowA attrs ^^^ \n', inflowA.print_attr())
    # print('\nInflowB attrs ^^^ \n ', inflowB.print_attr())
    print("\nIn ^^^", mat.__class__, out.print_attr())
    print("\nOut ^^^", out.__class__, out.print_attr())
    # Print data about reprocessing for current step
    print("\nBalance in %f t / out %f t" % (1e-6*mat.mass, 1e-6*out.mass))
    print("Removed FPs %f g" % (mat.mass-out.mass))
    print("Total waste %f g" % (waste[p[1]].mass + waste[p[2]].mass +
                                waste[p[3]].mass+waste[p[4]].mass))
    return out, waste


def refill(mat, refill_mass):
    """ Applies reprocessing scheme to selected material

    Parameters:
    -----------
    mat: Materialflow object`
        Material data right after reprocessing plant
    Returns:
    --------
    out: Materialflow object
        Material data after refill
    """
    feeds = read_feeds_from_input()
    ref = 'leu'
    # refill_mat = copy.deepcopy(feeds[ref])
    refill_mat = (refill_mass/feeds[ref].mass) * feeds[ref]
    out = mat + refill_mat
    print('Refilled fresh fuel %f g' % refill_mat.mass)
    """print(refill_mass)
    print(refill_mat)
    print(out)
    print(refill_mat.print_attr())
    print(mat.print_attr())
    print(out.print_attr())"""
    return out


def check_restart():
    if not restart_flag:
        try:
            os.remove(db_file)
            os.remove(iter_matfile)
            os.remove(input_file)
        except OSError as e:
            print("Error while deleting file, ", e)


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
    waste_st = {}
    mats_after_refill = {}
    for dts in range(steps):
        print ("\nStep #%i has been started" % (dts+1))
        if dts == 0:  # First step
            serpent.write_depcode_input(template_file, input_file)
            serpent.run_depcode(cores)
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dts
            mats = serpent.read_dep_comp(input_file, 0)  # 0)
            simulation.store_mat_data(mats, dts-1, 'before_reproc')
            # No reprocessing for initial composition but store it in h5 anyway
            simulation.store_mat_data(mats, dts-1, 'after_reproc')
        # Finish of First step
        # Main sequence
        else:
            serpent.run_depcode(cores)
        mats = serpent.read_dep_comp(input_file, 1)
        simulation.store_mat_data(mats, dts, 'before_reproc')
        simulation.store_run_step_info()
        # Reprocessing here
        nn_mat = 'fuel'
        mats_after_repr[nn_mat], waste_st[nn_mat] = reprocessing(mats[nn_mat])
        # Refill
        mats_after_refill[nn_mat] = refill(
                                        mats_after_repr[nn_mat],
                                        mats[nn_mat].mass -
                                        mats_after_repr[nn_mat].mass)
        print("\nMass of material before \
             %f g and after %f g" % (mats['fuel'].mass,
                                     mats_after_refill[nn_mat].mass))
        # Store in DB after reprocessing and refill (right before next depl)
        mats_after_refill['ctrlPois'] = mats['ctrlPois']
        simulation.store_mat_data(mats_after_refill, dts, 'after_reproc')
        serpent.write_mat_file(mats_after_refill,
                               iter_matfile,
                               dts)


if __name__ == "__main__":
    print('Initiating Saltproc:\n'
          '\tRestart = ' + str(restart_flag) + '\n'
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
    check_restart()
    main()
    print("\nSimulation succeeded.\n")
