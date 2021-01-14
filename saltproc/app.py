from saltproc import Depcode
from saltproc import Simulation
from saltproc import Materialflow
from saltproc import Process
from saltproc import Reactor
from saltproc import Sparger
from saltproc import Separator
# from depcode import Depcode
# from simulation import Simulation
# from materialflow import Materialflow
import os
import copy
import json
from collections import OrderedDict
import gc
import networkx as nx
import pydotplus
import argparse
import numpy as np


input_path = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(input_path, 'data/saltproc_tap')
iter_matfile = os.path.join(input_path, 'data/saltproc_mat')


def check_restart(restart_flag):
    """If the user set `Restart simulation from the step when it stopped?`
    for `False` clean out iteration files and database from previous run.

    Parameters
    ----------
    restart_flag : bool
        Is the current simulation restarted?
    """
    if not restart_flag:
        try:
            os.remove(db_file)
            os.remove(iter_matfile)
            os.remove(input_file)
            print("Previous run output files were deleted.")
        except OSError as e:
            pass


def parse_arguments():
    """Parses arguments from command line.

    Parameters
    -----------

    Returns
    --------
    n: int
        Number of nodes for use in Serpent simulation.
    d: int
        Number of cores for use in Serpent simulation.
    i: str
        Path and name of main SaltProc input file (json format).

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n',      # Number of nodes to use
                        type=int,
                        default=1,
                        help='number of cluster nodes to use in Serpent')
    parser.add_argument('-d',      # Number of nodes to use
                        type=int,
                        default=1,
                        help='number of threads to use in Serpent')
    parser.add_argument('-i',      # main input file
                        type=str,
                        default=None,
                        help='path and name of SaltProc main input file')
    args = parser.parse_args()
    return int(args.n), int(args.d), str(args.i)


def read_main_input(main_inp_file):
    """Reads main SaltProc input file (json format).

    Parameters
    -----------
    main_inp_file : str
        Path to SaltProc main input file and name of this file.
    """
    with open(main_inp_file) as f:
        j = json.load(f)
        global exec_path, spc_inp_file, dot_inp_file, template_file, db_file
        exec_path = j["Path to Serpent executable"]
        spc_inp_file = os.path.join(
                        os.path.dirname(f.name),
                        j["File containing processing system objects"])
        dot_inp_file = os.path.join(
                        os.path.dirname(f.name),
                        j["Graph file containing processing system structure"])
        template_file = os.path.join(
                        os.path.dirname(f.name),
                        j["User's Serpent input file with reactor model"])
        db_path = j["Path output data storing folder"]
        db_file = os.path.join(
                        os.path.dirname(f.name),
                        db_path,
                        j["Output HDF5 database file name"])
        # Read Monte Carlo setups
        global neutron_pop, active_cycles, inactive_cycles
        neutron_pop = j["Number of neutrons per generation"]
        active_cycles = j["Number of active generations"]
        inactive_cycles = j["Number of inactive generations"]
        # Read advanced simulatiion parameters
        global adjust_geo, restart_flag, core_massflow_rate
        adjust_geo = j["Switch to another geometry when keff drops below 1?"]
        restart_flag = j["Restart simulation from the step when it stopped?"]
        # Read paths to geometry files
        global geo_file
        if adjust_geo:
            geo_list = j["Geometry file/files to use in Serpent runs"]
            geo_file = [g for g in geo_list]
        elif not adjust_geo:
            geo_file = [j["Geometry file/files to use in Serpent runs"]]
        core_massflow_rate = \
            j["Salt mass flow rate throughout reactor core (g/s)"]
        global depl_hist, power_hist
        depl_hist = \
            j["Depletion step interval or Cumulative time (end of step) (d)"]
        power_hist = \
            j["Reactor power or power step list during depletion step (W)"]
        depsteps = \
            j["Number of steps for constant power and depletion interval case"]
        if depsteps is not None and isinstance(depl_hist, (float, int)):
            if depsteps < 0.0 or not int:
                raise ValueError('Depletion step interval cannot be negative')
            else:
                step = int(depsteps)
                deptot = float(depl_hist)*step
                depl_hist = np.linspace(float(depl_hist), deptot, num=step)
                power_hist = float(power_hist) * np.ones_like(depl_hist)
        elif depsteps is None and isinstance(depl_hist, (np.ndarray, list)):
            if len(depl_hist) != len(power_hist):
                raise ValueError(
                  'Depletion step list and power list shape mismatch')


def read_processes_from_input():
    """Parses ``removal`` data from `.json` file with `Process` objects
    description. Then returns dictionary of `Process` objects describing
    extraction process efficiency for each target chemical element.

    Returns
    -------
    mats : dict
        Dictionary that contains `Process` objects.

        ``key``
            Name of burnable material.
        ``value``
            `Process` object holding extraction process parameters.

    """
    processes = OrderedDict()
    with open(spc_inp_file) as f:
        j = json.load(f)
        for mat, value in j.items():
            processes[mat] = OrderedDict()
            for obj_name, obj_data in j[mat]['extraction_processes'].items():
                
                if obj_name == 'sparger':
                    j[mat]['extraction_processes'][obj_name]['efficiency'] =\
                    Sparger().eff()
                elif obj_name == 'entrainment_separator':
                    j[mat]['extraction_processes'][obj_name]['efficiency'] =\
                    Separator().eff()

            for obj_name, obj_data in j[mat]['extraction_processes'].items():
                
                print("Processs object data: ", obj_name, obj_data)
                processes[mat][obj_name] = Process(**obj_data)

        gc.collect()
        return processes


def read_feeds_from_input():
    """Parses ``feed`` data from `.json` file with `Materialflow` objects
    description. Then returns dictionary of `Materialflow` objects describing
    fresh fuel feeds.

    Returns
    -------
    mats : dict
        Dictionary that contains `Materialflow` objects with feeds.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object holding composition and properties of feed.
    """
    feeds = OrderedDict()
    with open(spc_inp_file) as f:
        j = json.load(f)
        # print(j['feeds'])
        for mat, val in j.items():
            feeds[mat] = OrderedDict()
            for obj_name, obj_data in j[mat]['feeds'].items():
                # print(obj_data)
                nucvec = obj_data['comp']
                feeds[mat][obj_name] = Materialflow(nucvec)
                feeds[mat][obj_name].mass = obj_data['mass']
                feeds[mat][obj_name].density = obj_data['density']
                feeds[mat][obj_name].vol = obj_data['volume']
        return feeds


def read_dot(dot_file):
    """Reads directed graph that describes fuel reprocessing system structure
    from `*.dot` file.

    Parameters
    ----------
    dot_file : str
        Path to `.dot` file with reprocessing system structure.

    Returns
    --------
    mat_name : str
        Name of burnable material which reprocessing scheme described in `.dot`
        file.
    paths_list : list
        List of lists containing all possible paths between `core_outlet` and
        `core_inlet`.

    """
    graph_pydot = pydotplus.graph_from_dot_file(dot_file)
    digraph = nx.drawing.nx_pydot.from_pydot(graph_pydot)
    mat_name = digraph.__str__()
    # iterate over all possible paths between 'core_outlet' and 'core_inlet'
    paths_list = []
    all_simple_paths = nx.all_simple_paths(digraph,
                                           source='core_outlet',
                                           target='core_inlet')
    for path in all_simple_paths:
        paths_list.append(path)
    return mat_name, paths_list


def reprocessing(mat):
    """Applies reprocessing scheme to burnable materials.

    Parameters
    -----------
    mats : dict
        Dictionary that contains `Materialflow` objects with burnable material
        data right after irradiation in the core.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object holding composition and properties.

    Returns
    --------
    waste : dict

        ``key``
            Process name.
        ``value``
            `Materialflow` object containing waste streams data.
    extracted_mass: dict

        ``key``
            Name of burnable material.
        ``value``
            Mass removed as waste in reprocessing function for each material
            (g).

    """
    inmass = {}
    extracted_mass = {}
    waste = OrderedDict()
    forked_mat = OrderedDict()
    prcs = read_processes_from_input()
    mat_name_dot, paths = read_dot(dot_inp_file)
    for mname in prcs.keys():  # iterate over materials
        waste[mname] = {}
        forked_mat[mname] = []
        inmass[mname] = float(mat[mname].mass)
        print("Material mass before reprocessing %f g" % inmass[mname])
        if mname == 'fuel' and mat_name_dot == 'fuel':
            w = 'waste_'
            ctr = 0
            for path in paths:
                forked_mat[mname].append(copy.deepcopy(mat[mname]))
                print("Material mass %f" % mat[mname].mass)
                for p in path:
                    # Calculate fraction of the flow going to the process p
                    divisor = float(prcs[mname][p].mass_flowrate /
                                    prcs[mname]['core_outlet'].mass_flowrate)
                    print('Process %s, divisor=%f' % (p, divisor))
                    # Update materialflow byt multiplying it by flow fraction
                    forked_mat[mname][ctr] = \
                        divisor * copy.deepcopy(forked_mat[mname][ctr])
                    waste[mname][w+p] = \
                        prcs[mname][p].rem_elements(forked_mat[mname][ctr])
                ctr += 1
            # Sum all forked material objects together
            mat[mname] = forked_mat[mname][0]  # initilize correct obj instance
            for idx in range(1, len(forked_mat[mname])):
                mat[mname] += forked_mat[mname][idx]
            print('1 Forked material mass %f' % (forked_mat[mname][0].mass))
            print('2 Forked material mass %f' % (forked_mat[mname][1].mass))
            print('\nMass balance %f g = %f + %f + %f + %f + %f + %f' %
                  (inmass[mname],
                   mat[mname].mass,
                   waste[mname]['waste_sparger'].mass,
                   waste[mname]['waste_entrainment_separator'].mass,
                   waste[mname]['waste_nickel_filter'].mass,
                   waste[mname]['waste_bypass'].mass,
                   waste[mname]['waste_liquid_metal'].mass))
        # Bootstrap for many materials
        if mname == 'ctrlPois':
            waste[mname]['removal_tb_dy'] = \
                prcs[mname]['removal_tb_dy'].rem_elements(mat[mname])
        extracted_mass[mname] = inmass[mname] - float(mat[mname].mass)
    del prcs, inmass, mname, forked_mat, mat_name_dot, paths, divisor
    return waste, extracted_mass


def refill(mat, extracted_mass, waste_dict):
    """Makes up material loss in removal processes by adding fresh fuel.

    Parameters
    -----------
    mat : dict

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object after performing all removals.
    extracted_mass: dict

        ``key``
            Name of burnable material.
        ``value``
            Mass removed as waste in reprocessing function for each material.
    waste : dict

        ``key``
            Process name.
        ``value``
            `Materialflow` object containing waste streams data.

    Returns
    --------
    dict
        Dictionary that contains `Materialflow` objects.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object after adding fresh fuel.
    """
    print('Fuel before refill ^^^', mat['fuel'].print_attr())
    feeds = read_feeds_from_input()
    refill_mat = OrderedDict()
    for mn, v in feeds.items():  # iterate over materials
        refill_mat[mn] = {}
        for feed_n, fval in feeds[mn].items():  # works with one feed only
            scale = extracted_mass[mn]/feeds[mn][feed_n].mass
            refill_mat[mn] = scale * feeds[mn][feed_n]
            waste_dict[mn]['feed_'+str(feed_n)] = refill_mat[mn]
        mat[mn] += refill_mat[mn]
        print('Refilled fresh material %s %f g' % (mn, refill_mat[mn].mass))
        print('Refill Material ^^^', refill_mat[mn].print_attr())
        print('Fuel after refill ^^^', mat[mn].print_attr())
    return waste_dict


def run():
    """ Inititializes main run.
    """
    # Parse arguments from command-lines
    nodes, cores, sp_input = parse_arguments()
    # Read main input file
    read_main_input(sp_input)
    # Print out input information
    print('Initiating Saltproc:\n'
          '\tRestart = ' + str(restart_flag) + '\n'
          '\tTemplate File Path  = ' + os.path.abspath(template_file) + '\n'
          '\tInput File Path     = ' + os.path.abspath(input_file) + '\n'
          '\tMaterial File Path  = ' + os.path.abspath(iter_matfile) + '\n'
          '\tOutput HDF5 DB Path = ' + os.path.abspath(db_file) + '\n'
          )
    # Intializing objects
    serpent = Depcode(
                codename='SERPENT',
                exec_path=exec_path,
                template_fname=template_file,
                input_fname=input_file,
                iter_matfile=iter_matfile,
                geo_file=geo_file,
                npop=neutron_pop,
                active_cycles=active_cycles,
                inactive_cycles=inactive_cycles)
    simulation = Simulation(
                sim_name='Super test',
                sim_depcode=serpent,
                core_number=cores,
                node_number=nodes,
                h5_file=db_file,
                iter_matfile=iter_matfile)
    msr = Reactor(
                volume=1.0,
                mass_flowrate=core_massflow_rate,
                power_levels=power_hist,
                depl_hist=depl_hist)
    # Check: Restarting previous simulation or starting new?
    check_restart(restart_flag)
    # Run sequence
    # Start sequence
    for dts in range(len(depl_hist)):
        print("\n\n\nStep #%i has been started" % (dts+1))
        serpent.write_depcode_input(template_file,
                                    input_file,
                                    msr,
                                    dts,
                                    restart_flag)
        serpent.run_depcode(cores, nodes)
        if dts == 0 and restart_flag is False:  # First step
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dts
            mats = serpent.read_dep_comp(input_file, 0)  # 0)
            simulation.store_mat_data(mats, dts-1, 'before_reproc')
        # Finish of First step
        # Main sequence
        mats = serpent.read_dep_comp(input_file, 1)
        simulation.store_mat_data(mats, dts, 'before_reproc')
        simulation.store_run_step_info()
        # Reprocessing here
        print("\nMass and volume of fuel before reproc %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois before reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_st, rem_mass = reprocessing(mats)
        print("\nMass and volume of fuel after reproc %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_feed_st = refill(mats, rem_mass, waste_st)
        print("\nMass and volume of fuel after REFILL %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after REFILL %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        print("Removed mass [g]:", rem_mass)
        # Store in DB after reprocessing and refill (right before next depl)
        simulation.store_after_repr(mats, waste_feed_st, dts)
        serpent.write_mat_file(mats, iter_matfile, simulation.burn_time)
        del mats, waste_st, waste_feed_st, rem_mass
        gc.collect()
        # Switch to another geometry?
        if adjust_geo and simulation.read_k_eds_delta(dts, restart_flag):
            simulation.switch_to_next_geometry()
        print("\nTime at the end of current depletion step %fd" %
              simulation.burn_time)
        print("Simulation succeeded.\n")
        '''print("Reactor object data.\n",
              msr.mass_flowrate,
              msr.power_levels,
              msr.depl_hist)'''
