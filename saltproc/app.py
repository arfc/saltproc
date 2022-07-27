from saltproc import DepcodeSerpent
from saltproc import DepcodeOpenMC
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
import jsonschema
from collections import OrderedDict
import gc
import networkx as nx
import pydotplus
import argparse
import numpy as np

def run():
    """ Inititializes main run.
    """
    nodes, cores, sp_input = parse_arguments()
    process_input_file, path_input_file, obj_inp = read_main_input(sp_input)
    _print_simulation_input_info(obj_in[1], obj_inp[0])
    # Intializing objects
    depcode = _create_depcode_object(obj_inp[0])
    simulation = _create_simulation_object(obj_inp[1])
    msr = _create_reactor_object(obj_inp[2])

    # Check: Restarting previous simulation or starting new?
    simulation.check_restart()
    # Run sequence
    # Start sequence
    for dep_step in range(len(msr.dep_step_length_cumulative)):
        print("\n\n\nStep #%i has been started" % (dep_step + 1))
        simulation.sim_depcode.write_depcode_input(msr,
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
        simulation.store_mat_data(mats, dep_step, False)
        simulation.store_run_step_info()
        # Reprocessing here
        print("\nMass and volume of fuel before reproc %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois before reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_st, rem_mass = reprocessing(mats, process_input_file, path_input_file)
        print("\nMass and volume of fuel after reproc %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_feed_st = refill(mats, rem_mass, waste_st, process_input_file)
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
            depcode.switch_to_next_geometry()
        print("\nTime at the end of current depletion step %fd" %
              simulation.burn_time)
        print("Simulation succeeded.\n")
        '''print("Reactor object data.\n",
        msr.mass_flowrate,
              msr.power_levels,
              msr.dep_step_length_cumulative)'''

def parse_arguments():
    """Parses arguments from command line.

    Parameters
    ----------

    Returns
    -------
    n: int
        Number of nodes for use in depletion code simulation.
    d: int
        Number of cores for use in depletion code simulation.
    i: str
        Path and name of main SaltProc input file (json format).

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n',      # Number of nodes to use
                        type=int,
                        default=1,
                        help='number of cluster nodes to use in \
                        depletion code simulation')
    parser.add_argument('-d',      # Number of cores to use
                        type=int,
                        default=1,
                        help='number of threads to use in \
                        depletion code simulation')
    parser.add_argument('-i',      # main input file
                        type=str,
                        default=None,
                        help='path and name of SaltProc main input file')
    args = parser.parse_args()
    return int(args.n), int(args.d), str(args.i)

def _process_main_input_reactor_params(reactor_input, num_depsteps):
    """
    Process SaltProc reactor class input parameters based on the value and
    data type of the `num_depsteps` parameter, and throw errors if the input
    parameters are incorrect.
    """
    dep_step_length_cumulative = reactor_input['dep_step_length_cumulative']
    power_levels = reactor_input['power_levels']
    if num_depsteps is not None and len(dep_step_length_cumulative) == 1:
        if num_depsteps < 0.0 or not int:
            raise ValueError('Depletion step interval cannot be negative')
        # Make `power_levels` and `dep_step_length_cumulative`
        # lists of length `num_depsteps`
        else:
            step = int(num_depsteps)
            deptot = float(dep_step_length_cumulative[0]) * step
            dep_step_length_cumulative = \
                np.linspace(float(dep_step_length_cumulative[0]),
                            deptot,
                            num=step)
            power_levels = float(power_levels[0]) * \
                np.ones_like(dep_step_length_cumulative)
            reactor_input['dep_step_length_cumulative'] = \
                dep_step_length_cumulative
            reactor_input['power_levels'] = power_levels
    elif num_depsteps is None and isinstance(dep_step_length_cumulative,
                                             (np.ndarray, list)):
        if len(dep_step_length_cumulative) != len(power_levels):
            raise ValueError(
                'Depletion step list and power list shape mismatch')

    return reactor_input


def read_main_input(main_inp_file):
    """Reads main SaltProc input file (json format).

    Parameters
    ----------
    main_inp_file : str
        Path to SaltProc main input file and name of this file.
    """

    input_schema = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                './input_schema.json')
    with open(main_inp_file) as f:
        j = json.load(f)
        with open(input_schema) as s:
            v = json.load(s)
            try:
                jsonschema.validate(instance=j, schema=v)
            except jsonschema.exceptions.ValidationError:
                print("Your input file improperly structured.\
                      Please see saltproc/tests/test.json for an example.")

        # Global input path
        path_prefix = os.getcwd()
        input_path = os.path.join(path_prefix, os.path.dirname(f.name))

        # Saltproc settings
        process_input_file = os.path.join(
            os.path.dirname(f.name),
            j['proc_input_file'])
        path_input_file = os.path.join(
            os.path.dirname(f.name),
            j['dot_input_file'])
        output_path = j['output_path']
        num_depsteps = j['num_depsteps']

        # Global output path
        output_path = os.path.join(input_path, output_path)
        j['output_path'] = output_path

        # Class settings
        depcode_input= j['depcode']
        simulation_input= j['simulation']
        reactor_input = j['reactor']

        if depcode_input['codename'] == 'serpent':
            depcode_input['template_input_file_path'] = os.path.join(
                input_path, depcode_input['template_input_file_path'])
        elif depcode_input['codename'] == 'openmc':
            for key in depcode_input['template_input_file_path']:
                value = depcode_input['template_input_file_path'][key]
                depcode_input['template_input_file_path'][key] = \
                    os.path.join(input_path, value)
        else:
            raise ValueError(
                f'{depcode_input["codename"]} is not a supported depletion code')

        geo_list = depcode_input['geo_file_paths']

        # Global geometry file paths
        geo_file_paths = []
        for g in geo_list:
            geo_file_paths += [os.path.join(input_path, g)]
        depcode_input['geo_file_paths'] = geo_file_paths

        # Global output file paths
        db_name = os.path.join(
            output_path, simulation_input['db_name'])
        simulation_input['db_name'] = db_name

        reactor_input = _process_main_input_reactor_params(reactor_input, num_depsteps)

        return process_input_file, path_input_file, (depcode_input, simulation_input, reactor_input)


def read_processes_from_input(process_input_file):
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
    with open(process_input_file) as f:
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


def read_feeds_from_input(process_input_file):
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
    with open(process_input_file) as f:
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
    -------
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


def reprocessing(mats, process_input_file, path_input_file):
    """Applies reprocessing scheme to burnable materials.

    Parameters
    ----------
    mats : dict of str to Materialflow
        Dictionary that contains `Materialflow` objects with burnable material
        data right after irradiation in the core.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object holding composition and properties.

    Returns
    -------
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
    prcs = read_processes_from_input(process_input_file)
    mats_name_dot, paths = read_dot(path_input_file)
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
            # initilize correct obj instance
            mats[mname] = forked_mats[mname][0]
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


def refill(mats, extracted_mass, waste_dict, process_input_file):
    """Makes up material loss in removal processes by adding fresh fuel.

    Parameters
    ----------
    mats : dict of str to Materialflow

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object after performing all removals.
    extracted_mass : dict of str to float

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
    -------
    refilled_mats: dict of str to Materialflow
        Dictionary that contains `Materialflow` objects.

        ``key``
            Name of burnable material.
        ``value``
            `Materialflow` object after adding fresh fuel.
    """
    print('Fuel before refill ^^^', mats['fuel'].print_attr())
    feeds = read_feeds_from_input(process_input_file)
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

def _create_depcode_object(depcode_input):
    """Helper function for `run()` """
    if depcode_input['codename'] == 'serpent':
        depcode = DepcodeSerpent(
            exec_path=depcode_input['exec_path'],
            template_inputfile_path=depcode_input['template_inputfile_path'],
            iter_inputfile=depcode_input['iter_inputfile'],
            iter_matfile=depcode_input['iter_matfile'],
            geo_files=depcode_input['geo_file_paths'],
            npop=depcode_input['npop'],
            active_cycles=depcode_input['active_cycles'],
            inactive_cycles=depcode_input['inactive_cycles'])
    else:
        raise ValueError(
            f'{depcode_input["codename"]} is not a supported depletion code')

    return depcode

def _create_simulation_object(simulation_input):
    """Helper function for `run()` """
    simulation = Simulation(
        sim_name='Super test',
        sim_depcode=depcode,
        core_number=cores,
        node_number=nodes,
        restart_flag=simulation_input['restart_flag'],
        adjust_geo=simulation_input['adjust_geo'],
        db_path=simulation_input['db_name'])
    return simulation


def _create_reactor_object(reactor_input):
    """Helper function for `run()` """
    msr = Reactor(
        volume=reactor_input['volume'],
        mass_flowrate=reactor_input['mass_flowrate'],
        power_levels=reactor_input['power_levels'],
        dep_step_length_cumulative=reactor_input['dep_step_length_cumulative'])
    return msr


def _print_simulation_input_info(simulation_input, depcode_input):
    """Helper function for `run()` """
    print('Initiating Saltproc:\n'
          '\tRestart = ' +
          str(simulation_input['restart_flag']) +
          '\n'
          '\tTemplate File Path  = ' +
          os.path.abspath(depcode_input['template_inputfile_path']) +
          '\n'
          '\tInput File Path     = ' +
          os.path.abspath(depcode_input['iter_inputfile']) +
          '\n'
          '\tMaterial File Path  = ' +
          os.path.abspath(depcode_input['iter_matfile']) +
          '\n'
          '\tOutput HDF5 database Path = ' +
          os.path.abspath(simulation_input['db_name']) +
          '\n')



