from saltproc import DepcodeSerpent
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
import json, jsonschema
from collections import OrderedDict
import gc
import networkx as nx
import pydotplus
import argparse
import numpy as np


input_path = os.getcwd()

input_schema = os.path.join(input_path, 'saltproc/input_schema.json')

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
        with open(input_schema) as v:
            s = json.load(v)
            try:
                jsonschema.validate(instance=j,schema=s)
            except jsonschema.exceptions.ValidationError:
                print("Your input file improperly structured. \
                      Please see saltproc/tests/test.json for an example.")

        # Saltproc settings
        global spc_inp_file, dot_inp_file, output_path, depsteps
        spc_inp_file = os.path.join(
            os.path.dirname(f.name),
            j['proc_input_file'])
        dot_inp_file = os.path.join(
            os.path.dirname(f.name),
            j['dot_input_file'])
        output_path = j['output_path']
        depsteps = j['depsteps']

        # Class settings
        global depcode_inp, simulation_inp, reactor_inp
        depcode_inp = j['depcode']
        simulation_inp = j['simulation']
        reactor_inp = j['reactor']

        depcode_inp['template_path'] = os.path.join(
            os.path.dirname(f.name), depcode_inp['template_path'])
        geo_list = depcode_inp['geo_files']
        geo_files = [g for g in geo_list]
        depcode_inp['geo_files'] = geo_list
        depcode_inp['iter_input_file'] = os.path.join(input_path, depcode_inp['iter_input_file'])
        depcode_inp['iter_matfile'] = os.path.join(input_path, depcode_inp['iter_matfile'])

        db_name = os.path.join(
            os.path.dirname(f.name),
            output_path, simulation_inp['db_name'])
        simulation_inp['db_name'] = db_name

        depl_hist = reactor_inp['depl_hist']
        power_levels = reactor_inp['power_levels']
        if depsteps is not None and isinstance(depl_hist, (float, int)):
            if depsteps < 0.0 or not int:
                raise ValueError('Depletion step interval cannot be negative')
            else:
                step = int(depsteps)
                deptot = float(depl_hist) * step
                depl_hist = np.linspace(float(depl_hist), deptot, num=step)
                power_levels = float(power_levels) * np.ones_like(depl_hist)
                reactor_inp['depl_hist'] = depl_hist
                reactor_inp['power_levels'] = power_levels
        elif depsteps is None and isinstance(depl_hist, (np.ndarray, list)):
            if len(depl_hist) != len(power_levels):
                raise ValueError(
                    'Depletion step list and power list shape mismatch')


def read_processes_from_input():
    """Parses ``removal`` data from `.json` file with `Process` objects
    description. Then returns dictionary of `Process` objects describing
    extraction process efficiency for each target chemical element.

    Returns
    -------
    mats : dict of str to Process
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
                print("Processs object data: ", obj_data)
                st = obj_data['efficiency']
                if obj_name == 'sparger' and st == "self":
                    processes[mat][obj_name] = Sparger(**obj_data)
                elif obj_name == 'entrainment_separator' and st == "self":
                    processes[mat][obj_name] = Separator(**obj_data)
                else:
                    processes[mat][obj_name] = Process(**obj_data)

        gc.collect()
        return processes


def read_feeds_from_input():
    """Parses ``feed`` data from `.json` file with `Materialflow` objects
    description. Then returns dictionary of `Materialflow` objects describing
    fresh fuel feeds.

    Returns
    -------
    mats : dict of str to Materialflow
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
    mat_name = digraph.name
    # iterate over all possible paths between 'core_outlet' and 'core_inlet'
    paths_list = []
    all_simple_paths = nx.all_simple_paths(digraph,
                                           source='core_outlet',
                                           target='core_inlet')
    for path in all_simple_paths:
        paths_list.append(path)
    return mat_name, paths_list


def reprocessing(mats):
    """Applies reprocessing scheme to burnable materials.

    Parameters
    -----------
    mats : dict of str to Materialflow
        Dictionary that contains `Materialflow` objects with burnable material
        data right after irradiation in the core.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object holding composition and properties.

    Returns
    --------
    waste : dict of str to Materialflow

        ``key``
            Process name.
        ``value``
            `Materialflow` object containing waste streams data.
    extracted_mass: dict of str to Materialflow

        ``key``
            Name of burnable material.
        ``value``
            Mass removed as waste in reprocessing function for each material
            (g).

    """
    inmass = {}
    extracted_mass = {}
    waste = OrderedDict()
    forked_mats = OrderedDict()
    prcs = read_processes_from_input()
    mats_name_dot, paths = read_dot(dot_inp_file)
    for mname in prcs.keys():  # iterate over materials
        waste[mname] = {}
        forked_mats[mname] = []
        inmass[mname] = float(mats[mname].mass)
        print("Material mass before reprocessing %f g" % inmass[mname])
        if mname == 'fuel' and mats_name_dot == 'fuel':
            w = 'waste_'
            ctr = 0
            for path in paths:
                forked_mats[mname].append(copy.deepcopy(mats[mname]))
                print("Material mass %f" % mats[mname].mass)
                for p in path:
                    # Calculate fraction of the flow going to the process p
                    divisor = float(prcs[mname][p].mass_flowrate /
                                    prcs[mname]['core_outlet'].mass_flowrate)
                    print('Process %s, divisor=%f' % (p, divisor))
                    # Update materialflow byt multiplying it by flow fraction
                    forked_mats[mname][ctr] = \
                        divisor * copy.deepcopy(forked_mats[mname][ctr])
                    waste[mname][w + p] = \
                        prcs[mname][p].rem_elements(forked_mats[mname][ctr])
                ctr += 1
            # Sum all forked material objects together
            mats[mname] = forked_mats[mname][0]  # initilize correct obj instance
            for idx in range(1, len(forked_mats[mname])):
                mats[mname] += forked_mats[mname][idx]
            print('1 Forked material mass %f' % (forked_mats[mname][0].mass))
            print('2 Forked material mass %f' % (forked_mats[mname][1].mass))
            print('\nMass balance %f g = %f + %f + %f + %f + %f + %f' %
                  (inmass[mname],
                   mats[mname].mass,
                   waste[mname]['waste_sparger'].mass,
                   waste[mname]['waste_entrainment_separator'].mass,
                   waste[mname]['waste_nickel_filter'].mass,
                   waste[mname]['waste_bypass'].mass,
                   waste[mname]['waste_liquid_metal'].mass))
        # Bootstrap for many materials
        if mname == 'ctrlPois':
            waste[mname]['removal_tb_dy'] = \
                prcs[mname]['removal_tb_dy'].rem_elements(mats[mname])
        extracted_mass[mname] = inmass[mname] - float(mats[mname].mass)
    del prcs, inmass, mname, forked_mats, mats_name_dot, paths, divisor
    return waste, extracted_mass


def refill(mats, extracted_mass, waste_dict):
    """Makes up material loss in removal processes by adding fresh fuel.

    Parameters
    -----------
    mats : dict of str to Materialflow

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object after performing all removals.
    extracted_mass: dict of str to float

        ``key``
            Name of burnable material.
        ``value``
            Mass removed as waste in reprocessing function for each material.
    waste_dict : dict of str to Materialflow

        ``key``
            Process name.
        ``value``
            `Materialflow` object containing waste streams data.

    Returns
    --------
    refilled_mats: dict of str to Materialflow
        Dictionary that contains `Materialflow` objects.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object after adding fresh fuel.
    """
    print('Fuel before refill ^^^', mats['fuel'].print_attr())
    feeds = read_feeds_from_input()
    refill_mats = OrderedDict()
    for mn, v in feeds.items():  # iterate over materials
        refill_mats[mn] = {}
        for feed_n, fval in feeds[mn].items():  # works with one feed only
            scale = extracted_mass[mn] / feeds[mn][feed_n].mass
            refill_mats[mn] = scale * feeds[mn][feed_n]
            waste_dict[mn]['feed_' + str(feed_n)] = refill_mats[mn]
        mats[mn] += refill_mats[mn]
        print('Refilled fresh material %s %f g' % (mn, refill_mats[mn].mass))
        print('Refill Material ^^^', refill_mats[mn].print_attr())
        print('Fuel after refill ^^^', mats[mn].print_attr())
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
          '\tRestart = ' + str(simulation_inp['restart_flag']) + '\n'
          '\tTemplate File Path  = ' + os.path.abspath(depcode_inp['template_path']) + '\n'
          '\tInput File Path     = ' + os.path.abspath(depcode_inp['iter_input_file']) + '\n'
          '\tMaterial File Path  = ' + os.path.abspath(depcode_inp['iter_matfile']) + '\n'
          '\tOutput HDF5 DB Path = ' + os.path.abspath(simulation_inp['db_name']) + '\n'
          )
    # Intializing objects
    if depcode_inp['codename'] == 'serpent':
        depcode = DepcodeSerpent(
            exec_path=depcode_inp['exec_path'],
            template_path=depcode_inp['template_path'],
            iter_input_file=depecode_inp['iter_input_file'],
            iter_matfile=depcode_inp['iter_matfile'],
            geo_files=depcode_inp['geo_files'],
            npop=depcode_inp['npop'],
            active_cycles=depcode_inp['active_cycles'],
            inactive_cycles=depcode_inp['inactive_cycles'])
    else:
        raise ValueError(f'{depcode_inp["codename"]} is not a supported depletion code')

    simulation = Simulation(
        sim_name='Super test',
        sim_depcode=depcode,
        core_number=cores,
        node_number=nodes,
        db_path=simulation_inp['db_name'])

    msr = Reactor(
        volume=reactor_inp['volume'],
        mass_flowrate=reactor_inp['mass_flowrate'],
        power_levels=reactor_inp['power_levels'],
        depl_hist=reactor_inp['depl_hist'])
    # Check: Restarting previous simulation or starting new?
    simulation.check_restart()
    # Run sequence
    # Start sequence
    for dep_step in range(len(reactor.depl_hist)):
        print("\n\n\nStep #%i has been started" % (dep_step + 1))
        simulation.depcode.write_depcode_input(msr,
                                    dep_step,
                                    simulation.restart_flag)
        depcode.run_depcode(cores, nodes)
        if dep_step == 0 and simulation.restart_flag is False:  # First step
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dep_step)
            mats = depcode.read_dep_comp(False)
            simulation.store_mat_data(mats, dep_step - 1, False)
        # Finish of First step
        # Main sequence
        mats = depcode.read_dep_comp(True)
        simulation.store_mat_data(mats, dep_step, True)
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
        simulation.store_after_repr(mats, waste_feed_st, dep_step)
        depcode.write_mat_file(mats, simulation.burn_time)
        del mats, waste_st, waste_feed_st, rem_mass
        gc.collect()
        # Switch to another geometry?
        if simulation.adjust_geo and simulation.read_k_eds_delta(dep_step):
            simulation.switch_to_next_geometry()
        print("\nTime at the end of current depletion step %fd" %
              simulation.burn_time)
        print("Simulation succeeded.\n")
        '''print("Reactor object data.\n",
              msr.mass_flowrate,
              msr.power_levels,
              msr.depl_hist)'''
