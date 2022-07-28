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
    # Parse arguments from command-lines
    nodes, cores, sp_input = parse_arguments()
    # Read main input file
    read_main_input(sp_input)
    if depcode_inp['codename'] == 'serpent':
        template_file_path = \
            os.path.abspath(depcode_inp['template_input_file_path'])
    elif depcode_inp['codename'] == 'openmc':
        template_file_path = \
            os.path.dirname(
                os.path.abspath(
                    depcode_inp['template_input_file_path']['materials']))
    iter_file_path = os.path.abspath(output_path)
    # Print out input information
    print('Initiating Saltproc:\n'
          '\tRestart = ' +
          str(simulation_inp['restart_flag']) +
          '\n'
          '\tTemplate File Path(s)  = ' +
          template_file_path +
          '\n'
          '\tDepletion Step File Path     = ' +
          iter_file_path +
          '\n'
          '\tOutput HDF5 database Path = ' +
          os.path.abspath(simulation_inp['db_name']) +
          '\n')
    # Intializing objects
    if depcode_inp['codename'] == 'serpent':
        iter_inputfile = os.path.join(
            output_path, 'serpent_iter_input.serpent')
        iter_matfile = os.path.join(
            output_path, 'serpent_iter_matfile.ini')
        depcode = DepcodeSerpent()
    elif depcode_inp['codename'] == 'openmc':
        iter_inputfile = {}
        for key in depcode_inp['template_input_file_path']:
            iter_inputfile[key] = \
                os.path.join(output_path, key + '.xml')

        iter_matfile = os.path.join(output_path, 'materals.xml')
        depcode = DepcodeOpenMC()
    else:
        raise ValueError(
            f'{depcode_inp["codename"]} is not a supported depletion code')

    depcode.template_input_file_path = depcode_inp['template_input_file_path']
    depcode.geo_files = depcode_inp['geo_file_paths']
    depcode.npop = depcode_inp['npop']
    depcode.active_cycles = depcode_inp['active_cycles']
    depcode.inactive_cycles = depcode_inp['inactive_cycles']

    depcode.iter_inputfile = iter_inputfile
    depcode.iter_matfile = iter_matfile

    simulation = Simulation(
        sim_name='Super test',
        sim_depcode=depcode,
        core_number=cores,
        node_number=nodes,
        restart_flag=simulation_inp['restart_flag'],
        adjust_geo=simulation_inp['adjust_geo'],
        db_path=simulation_inp['db_name'])

    msr = Reactor(
        volume=reactor_inp['volume'],
        mass_flowrate=reactor_inp['mass_flowrate'],
        power_levels=reactor_inp['power_levels'],
        dep_step_length_cumulative=reactor_inp['dep_step_length_cumulative'])
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
        print("\nMass and volume of fuel before reproc: %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois before reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_streams, extracted_mass = reprocess_materials(mats)
        print("\nMass and volume of fuel after reproc: %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_and_feed_streams = refill_materials(mats,
                                                  extracted_mass,
                                                  waste_streams)
        print("\nMass and volume of fuel after REFILL: %f g; %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after REFILL %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        print("Removed mass [g]:", extracted_mass)
        # Store in DB after reprocessing and refill (right before next depl)
        simulation.store_after_repr(mats, waste_and_feed_streams, dep_step)
        depcode.write_mat_file(mats, simulation.burn_time)
        del mats, waste_streams, waste_feed_st, extracted_mass
        gc.collect()
        # Switch to another geometry?
        if simulation.adjust_geo and simulation.read_k_eds_delta(dep_step):
            depcode.switch_to_next_geometry()
        print("\nTime at the end of current depletion step: %fd" %
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
        global spc_inp_file, dot_inp_file, output_path, num_depsteps
        spc_inp_file = os.path.join(
            os.path.dirname(f.name),
            j['proc_input_file'])
        dot_inp_file = os.path.join(
            os.path.dirname(f.name),
            j['dot_input_file'])
        output_path = j['output_path']
        num_depsteps = j['num_depsteps']

        # Global output path
        output_path = os.path.join(input_path, output_path)
        j['output_path'] = output_path

        # Class settings
        global depcode_inp, simulation_inp, reactor_inp
        depcode_inp = j['depcode']
        simulation_inp = j['simulation']
        reactor_inp = j['reactor']

        if depcode_inp['codename'] == 'serpent':
            depcode_inp['template_input_file_path'] = os.path.join(
                input_path, depcode_inp['template_input_file_path'])
        elif depcode_inp['codename'] == 'openmc':
            for key in depcode_inp['template_input_file_path']:
                value = depcode_inp['template_input_file_path'][key]
                depcode_inp['template_input_file_path'][key] = \
                    os.path.join(input_path, value)
        else:
            raise ValueError(
                f'{depcode_inp["codename"]} is not a supported depletion code')

        geo_list = depcode_inp['geo_file_paths']

        # Global geometry file paths
        geo_file_paths = []
        for g in geo_list:
            geo_file_paths += [os.path.join(input_path, g)]
        depcode_inp['geo_file_paths'] = geo_file_paths

        # Global output file paths
        db_name = os.path.join(
            output_path, simulation_inp['db_name'])
        simulation_inp['db_name'] = db_name

        dep_step_length_cumulative = reactor_inp['dep_step_length_cumulative']
        power_levels = reactor_inp['power_levels']
        if num_depsteps is not None and len(dep_step_length_cumulative) == 1:
            if num_depsteps < 0.0 or not int:
                raise ValueError('Depletion step interval cannot be negative')
            else:
                step = int(num_depsteps)
                deptot = float(dep_step_length_cumulative[0]) * step
                dep_step_length_cumulative = \
                    np.linspace(float(dep_step_length_cumulative[0]),
                                deptot,
                                num=step)
                power_levels = float(power_levels[0]) * \
                    np.ones_like(dep_step_length_cumulative)
                reactor_inp['dep_step_length_cumulative'] = \
                    dep_step_length_cumulative
                reactor_inp['power_levels'] = power_levels
        elif num_depsteps is None and isinstance(dep_step_length_cumulative,
                                                 (np.ndarray, list)):
            if len(dep_step_length_cumulative) != len(power_levels):
                raise ValueError(
                    'Depletion step list and power list shape mismatch')


def reprocess_materials(mats):
    """Applies extraction reprocessing scheme to burnable materials.

    Parameters
    ----------
    mats : dict of str to Materialflow
        Dictionary that contains :class:`saltproc.materialflow.Materialflow`
        objects with burnable material data right after irradiation in the
        core.

    Returns
    -------
    waste_streams : dict of str to dict
        Dictionary mapping material names to waste streams.

        ``key``
            Material name.
        ``value``
            Dictionary mapping waste stream names to
            :class:`saltproc.materialflow.Materialflow`
            objects representing waste streams.
    extracted_mass: dict of str to float
        Dictionary mapping material names to the mass in [g] of that material
        removed via reprocessing.

    """
    inmass = {}
    extracted_mass = {}
    waste_streams = OrderedDict()
    thru_flows = OrderedDict()

    extraction_processes = get_extraction_processes()
    material_for_extraction, extraction_process_paths = \
        get_extraction_process_paths(dot_inp_file)

    # iterate over materials
    for mat_name, processes in extraction_processes.items():
        initial_material = mats[mat_name]
        waste_streams[mat_name] = {}
        thru_flows[mat_name] = []

        inmass[mat_name] = float(initial_material.mass)
        print(f"Mass of material '{mat_name}' before reprocessing: "
              f"{inmass[mat_name]} g")

        if mat_name == 'fuel' and material_for_extraction == 'fuel':
            for i, path in enumerate(extraction_process_paths):
                thru_flows[mat_name].append(initial_material)

                for proc in path:
                    # Calculate fraction of the flow going to the process proc
                    divisor = float(processes[proc].mass_flowrate /
                                    processes['core_outlet'].mass_flowrate)
                    print(f'Process: {proc}, divisor={divisor}')

                    # Calculate waste stream and thru flow on proccess proc
                    thru_flow, waste_stream = \
                        processes[proc].process_material(
                            divisor * thru_flows[mat_name][i])

                    waste_streams[mat_name]['waste_' + proc] = waste_stream
                    thru_flows[mat_name][i] = thru_flow

            # Sum thru flows from all paths together
            mats[mat_name] = thru_flows[mat_name][0]
            print(f'1 Materal mass on path 0:'
                  f'{thru_flows[mat_name][0].mass}')
            for idx in range(1, i + 1):
                mats[mat_name] += thru_flows[mat_name][idx]
                print(f'{i + 1} Materal mass on path {i}:'
                      f'{thru_flows[mat_name][i].mass}')

            print('\nMass balance: %f g = %f + %f + %f + %f + %f + %f' %
                  (inmass[mat_name],
                   mats[mat_name].mass,
                   waste_streams[mat_name]['waste_sparger'].mass,
                   waste_streams[mat_name]['waste_entrainment_separator'].mass,
                   waste_streams[mat_name]['waste_nickel_filter'].mass,
                   waste_streams[mat_name]['waste_bypass'].mass,
                   waste_streams[mat_name]['waste_liquid_metal'].mass))

        # Bootstrap for many materials
        if mat_name == 'ctrlPois':
            thru_flow, waste_stream = \
                processes['removal_tb_dy'].process_material(mats[mat_name])

            waste_streams[mat_name]['removal_tb_dy'] = waste_stream
            mats[mat_name] = thru_flow

        extracted_mass[mat_name] = \
            inmass[mat_name] - float(mats[mat_name].mass)

    # Clear memory
    del extraction_processes, inmass, mat_name, processes, thru_flows
    del material_for_extraction, extraction_process_paths, divisor
    del thru_flow, waste_stream

    return waste_streams, extracted_mass


def get_extraction_processes():
    """Parses ``extraction_processes`` objects from the `.json` file describing
    processing system objects.

    ``extraction_processes`` objects describe components that would perform
    fuel processing in a real reactor, such as a gas sparger or a nickel
    filter.

    Returns
    -------
    extraction_processes : dict of str to dict
        Dictionary mapping material names to extraction processes.

        ``key``
            Name of burnable material.
        ``value``
            Dictionary mapping process names to
            :class:`saltproc.process.Process` objects.

    """
    extraction_processes = OrderedDict()
    with open(spc_inp_file) as f:
        j = json.load(f)
        for mat_name, procs in j.items():
            extraction_processes[mat_name] = OrderedDict()
            for proc_name, proc_data in procs['extraction_processes'].items():
                print("Processs object data: ", proc_data)
                st = proc_data['efficiency']
                if proc_name == 'sparger' and st == "self":
                    extraction_processes[mat_name][proc_name] = \
                        Sparger(**proc_data)
                elif proc_name == 'entrainment_separator' and st == "self":
                    extraction_processes[mat_name][proc_name] = \
                        Separator(**proc_data)
                else:
                    extraction_processes[mat_name][proc_name] = \
                        Process(**proc_data)

        gc.collect()
        return extraction_processes


def get_extraction_process_paths(dot_file):
    """Reads directed graph that describes fuel reprocessing system structure
    from a `*.dot` file.

    Parameters
    ----------
    dot_file : str
        Path to `.dot` file with reprocessing system structure.

    Returns
    -------
    mat_name : str
        Name of burnable material which the reprocessing scheme applies to.
    extraction_process_paths : list
        List of lists containing all possible paths between `core_outlet` and
        `core_inlet`.

    """
    graph_pydot = pydotplus.graph_from_dot_file(dot_file)
    digraph = nx.drawing.nx_pydot.from_pydot(graph_pydot)
    mat_name = digraph.name
    # Iterate over all possible paths between 'core_outlet' and 'core_inlet'
    all_simple_paths = nx.all_simple_paths(digraph,
                                           source='core_outlet',
                                           target='core_inlet')
    extraction_process_paths = []
    for path in all_simple_paths:
        extraction_process_paths.append(path)
    return mat_name, extraction_process_paths


def refill_materials(mats, extracted_mass, waste_streams):
    """Makes up material loss in removal processes by adding fresh fuel.

    Parameters
    ----------
    mats : dict of str to Materialflow
        Dicitionary mapping material names to
        :class:`saltproc.materialflow.Materialflow` objects that have already
        been reprocessed by `reprocess_materials`.

    extracted_mass : dict of str to float
        Dictionary mapping material names to the mass in [g] of that material
        removed via reprocessing.
    waste_streams : dict of str to dict
        Dictionary mapping material names to waste streams from reprocessing

        ``key``
            Material name.
        ``value``
            Dictionary mapping waste stream names to
            :class:`saltproc.materialflow.Materialflow` objects representing
            waste streams.

    Returns
    -------
    waste_streams : dict of str to dict
        Superset of the input parameter `waste_streams`. Dictionary has
        keys for feed streams that map to :classs:`Materialflow` objects
        representing those material feed streams.

    """
    print('Fuel before refilling: ^^^', mats['fuel'].print_attr())
    feeds = get_feeds()
    refill_mats = OrderedDict()
    # Get feed group for each material
    for mat, mat_feeds in feeds.items():
        refill_mats[mat] = {}
        # Get each feed in the feed group
        for feed_name, feed in mat_feeds.items():
            scale = extracted_mass[mat] / feed.mass
            refill_mats[mat] = scale * feed
            waste_streams[mat]['feed_' + str(feed_name)] = refill_mats[mat]
        mats[mat] += refill_mats[mat]
        print('Refilled fresh material: %s %f g' %
              (mat, refill_mats[mat].mass))
        print('Refill Material: ^^^', refill_mats[mat].print_attr())
        print('Fuel after refill: ^^^', mats[mat].print_attr())
    return waste_streams


def get_feeds():
    """Parses ``feed`` objects from `.json` file describing processing system
    objects.

    ``feed`` objects describe material flows that replace nuclides needed to
    keep the reactor operating that were removed during reprocessing.

    Returns
    -------
    feeds : dict of str to dict
        Dictionary that maps material names to material flows
        ``key``
            Name of burnable material.
        ``value``
            Dictionary mapping material flow names to
            :class:`saltproc.materialflow.Materialflow` objects representing
            material feeds.

    """
    feeds = OrderedDict()
    with open(spc_inp_file) as f:
        j = json.load(f)
        for mat in j:
            feeds[mat] = OrderedDict()
            for feed_name, feed_data in j[mat]['feeds'].items():
                nucvec = feed_data['comp']
                feeds[mat][feed_name] = Materialflow(nucvec)
                feeds[mat][feed_name].mass = feed_data['mass']
                feeds[mat][feed_name].density = feed_data['density']
                feeds[mat][feed_name].vol = feed_data['volume']
        return feeds
