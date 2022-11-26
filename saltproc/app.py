from pathlib import Path
from copy import deepcopy
from collections import OrderedDict

import argparse
import numpy as np
import json
import jsonschema
import gc
import networkx as nx
import pydotplus

from saltproc import SerpentDepcode, OpenMCDepcode, Simulation, Reactor
from saltproc import Process, Sparger, Separator, Materialflow


def run():
    """ Inititializes main run"""
    nodes, cores, saltproc_input = parse_arguments()
    input_path, process_file, dot_file, object_input = \
        read_main_input(saltproc_input)
    _print_simulation_input_info(object_input[1], object_input[0])
    # Intializing objects
    depcode = _create_depcode_object(object_input[0])
    simulation = _create_simulation_object(
        object_input[1], depcode, cores, nodes)
    msr = _create_reactor_object(object_input[2])

    if isinstance(depcode.runtime_inputfile, str):
        depcode.runtime_inputfile = (input_path /
                                  depcode.runtime_inputfile).resolve().as_posix()
    else:
        raise ValueError("not implemented")
    depcode.runtime_matfile = (
        input_path /
        depcode.runtime_matfile).resolve().as_posix()
    # Check: Restarting previous simulation or starting new?
    simulation.check_restart()
    # Run sequence
    # Start sequence
    for dep_step in range(len(msr.dep_step_length_cumulative)):
        print("\n\n\nStep #%i has been started" % (dep_step + 1))
        simulation.sim_depcode.write_depcode_input(msr,
                                                   dep_step,
                                                   simulation.restart_flag)
        depcode.run_depletion_step(cores, nodes)
        if dep_step == 0 and simulation.restart_flag is False:  # First step
            # Read general simulation data which never changes
            simulation.store_run_init_info()
            # Parse and store data for initial state (beginning of dep_step)
            mats = depcode.read_depleted_materials(False)
            simulation.store_mat_data(mats, dep_step - 1, False)
        # Finish of First step
        # Main sequence
        mats = depcode.read_depleted_materials(True)
        simulation.store_mat_data(mats, dep_step, False)
        simulation.store_run_step_info()
        # Reprocessing here
        print("\nMass and volume of fuel before reproc: %f g, %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois before reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_streams, extracted_mass = reprocess_materials(mats,
                                                            process_file,
                                                            dot_file)
        print("\nMass and volume of fuel after reproc: %f g, %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after reproc %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        waste_and_feed_streams = refill_materials(mats,
                                                  extracted_mass,
                                                  waste_streams,
                                                  process_file)
        print("\nMass and volume of fuel after REFILL: %f g, %f cm3" %
              (mats['fuel'].mass,
               mats['fuel'].vol))
        # print("Mass and volume of ctrlPois after REFILL %f g; %f cm3" %
        #       (mats['ctrlPois'].mass,
        #        mats['ctrlPois'].vol))
        print("Removed mass [g]:", extracted_mass)
        # Store in DB after reprocessing and refill (right before next depl)
        simulation.store_after_repr(mats, waste_and_feed_streams, dep_step)
        depcode.update_depletable_materials(mats, simulation.burn_time)
        del mats, waste_streams, waste_and_feed_streams, extracted_mass
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

    Returns
    -------
    input_path : PosixPath
        Path to main input file
    process_file : str
        Path to the `.json` file describing the fuel reprocessing components.
    dot_file : str
        Path to the `.dot` describing the fuel reprocessing paths.
    object_inputs : 3-tuple of dict
        tuple containing the inputs for constructing the
        :class:`~saltproc.Depcode`, :class:`~saltproc.Simulation`, and
        :class:`~saltproc.Reactor` objects.

    """

    input_schema = (Path(__file__).parents[0] / 'input_schema.json')
    with open(main_inp_file) as f:
        j = json.load(f)
        with open(input_schema) as s:
            v = json.load(s)
            try:
                jsonschema.validate(instance=j, schema=v)
            except jsonschema.exceptions.ValidationError:
                print("Your input file is improperly structured.\
                      Please see saltproc/tests/test.json for an example.")

        # Global input path
        input_path = (Path.cwd() / Path(f.name).parents[0])

        # Saltproc settings
        process_file = (input_path /
                              j['proc_input_file']).resolve().as_posix()
        dot_file = (
            input_path /
            j['dot_input_file']).resolve().as_posix()
        output_path = j['output_path']
        num_depsteps = j['num_depsteps']

        # Global output path
        output_path = (input_path / output_path)
        j['output_path'] = output_path.resolve()

        # Class settings
        depcode_input = j['depcode']
        simulation_input = j['simulation']
        reactor_input = j['reactor']

        if depcode_input['codename'] == 'serpent':
            depcode_input['template_input_file_path'] = (
                input_path /
                depcode_input['template_input_file_path']).resolve().as_posix()
        elif depcode_input['codename'] == 'openmc':
            for key in depcode_input['template_input_file_path']:
                value = depcode_input['template_input_file_path'][key]
                depcode_input['template_input_file_path'][key] = (
                    input_path / value).resolve().as_posix()
        else:
            raise ValueError(
                f'{depcode_input["codename"]} '
                'is not a supported depletion code')

        geo_list = depcode_input['geo_file_paths']

        # Global geometry file paths
        geo_file_paths = []
        for g in geo_list:
            geo_file_paths += [(input_path / g).resolve().as_posix()]
        depcode_input['geo_file_paths'] = geo_file_paths

        # Global output file paths
        db_name = (output_path / simulation_input['db_name'])
        simulation_input['db_name'] = db_name.resolve().as_posix()

        reactor_input = _process_main_input_reactor_params(
            reactor_input, num_depsteps)

        return input_path, process_file, dot_file, (
            depcode_input, simulation_input, reactor_input)


def _print_simulation_input_info(simulation_input, depcode_input):
    """Helper function for `run()` """
    print('Initiating Saltproc:\n'
          '\tRestart = ' +
          str(simulation_input['restart_flag']) +
          '\n'
          '\tTemplate File Path  = ' +
          depcode_input['template_input_file_path'] +
          '\n'
          '\tOutput HDF5 database Path = ' +
          simulation_input['db_name'] +
          '\n')


def _create_depcode_object(depcode_input):
    """Helper function for `run()` """
    codename = depcode_input['codename']
    if codename == 'serpent':
        depcode = SerpentDepcode
    elif codename == 'openmc':
        depcode = OpenMCDepcode
    else:
        raise ValueError(
            f'{depcode_input["codename"]} is not a supported depletion code')

    depcode = depcode(depcode_input['exec_path'],
                      depcode_input['template_input_file_path'],
                      geo_files=depcode_input['geo_file_paths'],
                      npop=depcode_input['npop'],
                      active_cycles=depcode_input['active_cycles'],
                      inactive_cycles=depcode_input['inactive_cycles'])

    return depcode


def _create_simulation_object(simulation_input, depcode, cores, nodes):
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


def reprocess_materials(mats, process_file, dot_file):
    """Applies extraction reprocessing scheme to burnable materials.

    Parameters
    ----------
    mats : dict of str to Materialflow
        Dictionary that contains :class:`saltproc.materialflow.Materialflow`
        objects with burnable material data right after irradiation in the
        core.
    process_file : str
        Path to the `.json` file describing the fuel reprocessing components.
    dot_file : str
        Path to the `.dot` describing the fuel reprocessing paths.

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

    extraction_processes = get_extraction_processes(process_file)
    material_for_extraction, extraction_process_paths = \
        get_extraction_process_paths(dot_file)

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
            print(f'1 Materal mass on path 0: '
                  f'{thru_flows[mat_name][0].mass}')
            for idx in range(1, i + 1):
                mats[mat_name] += thru_flows[mat_name][idx]
                print(f'{i + 1} Materal mass on path {i}: '
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


def get_extraction_processes(process_file):
    """Parses ``extraction_processes`` objects from the `.json` file describing
    processing system objects.

    ``extraction_processes`` objects describe components that would perform
    fuel processing in a real reactor, such as a gas sparger or a nickel
    filter.

    Parameters
    ----------
    process_file : str
        Path to the `.json` file describing the fuel reprocessing components.

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
    with open(process_file) as f:
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
        Path to the `.dot` describing the fuel reprocessing paths.

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


def refill_materials(mats, extracted_mass, waste_streams, process_file):
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
    process_file : str
        Path to the `.json` file describing the fuel reprocessing components.

    Returns
    -------
    waste_streams : dict of str to dict
        Superset of the input parameter `waste_streams`. Dictionary has
        keys for feed streams that map to :classs:`Materialflow` objects
        representing those material feed streams.

    """
    print('Fuel before refilling: ^^^', mats['fuel'].print_attr())
    feeds = get_feeds(process_file)
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


def get_feeds(process_file):
    """Parses ``feed`` objects from `.json` file describing processing system
    objects.

    ``feed`` objects describe material flows that replace nuclides needed to
    keep the reactor operating that were removed during reprocessing.

    Parameters
    ----------
    process_file : str
        Path to the `.json` file describing the fuel reprocessing components.

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
    with open(process_file) as f:
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
