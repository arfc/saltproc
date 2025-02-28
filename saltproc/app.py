import os
from pathlib import Path
from copy import deepcopy

from collections import OrderedDict

import argparse
import numpy as np
import traceback
import json, jsonschema
import gc
import networkx as nx

from saltproc import SerpentDepcode, OpenMCDepcode, Simulation, Reactor
from saltproc import Process, Sparger, Separator, Materialflow

# Validator that fills defualt values of JSON schema before validating
from saltproc._schema_default import DefaultFillingValidator


CODENAME_MAP = {'serpent': SerpentDepcode,
                 'openmc': OpenMCDepcode}

SECOND_UNITS = ('s', 'sec')
MINUTE_UNITS = ('min', 'minute')
HOUR_UNITS = ('h', 'hr', 'hour')
DAY_UNITS = ('d', 'day')
YEAR_UNITS = ('a', 'year', 'yr')

_SECONDS_PER_DAY = 60 * 60 * 24
_MINUTES_PER_DAY = 60 * 24
_HOURS_PER_DAY = 24
_DAYS_PER_YEAR = 365.25

def run():
    """ Inititializes main run"""
    threads, saltproc_input = parse_arguments()
    input_path, process_file, dot_file, mpi_args, \
        rebuild_saltproc_results, run_without_reprocessing, object_input = \
        read_main_input(saltproc_input)
    _print_simulation_input_info(object_input[1], object_input[0])
    # Intializing objects
    depcode = _create_depcode_object(object_input[0])
    simulation = _create_simulation_object(
        object_input[1], depcode)
    msr = _create_reactor_object(object_input[2])

    # Check: Restarting previous simulation or starting new?
    failed_step = simulation.check_restart()
    # Run sequence
    # Start sequence
    for step_idx in range(failed_step, len(msr.depletion_timesteps)):
        print("\n\n\nStep #%i has been started" % (step_idx + 1))
        simulation.sim_depcode.write_runtime_input(msr,
                                                   step_idx,
                                                   simulation.restart_flag)

        if rebuild_saltproc_results:
            simulation.sim_depcode.rebuild_simulation_files(step_idx)
        else:
            depcode.run_depletion_step(mpi_args, threads)
        if step_idx == 0 and simulation.restart_flag is False:  # First step
            # Read general simulation data which never changes
            simulation.store_depcode_metadata()
            # Parse and store data for initial state (beginning of step_idx)
            mats = depcode.read_depleted_materials(False)
            simulation.store_mat_data(mats, step_idx - 1, False)
        # Finish of First step
        # Main sequence
        mats = depcode.read_depleted_materials(True)
        simulation.store_mat_data(mats, step_idx, False)
        simulation.store_step_neutronics_parameters()
        simulation.store_step_metadata()

        # Reprocessing here
        if run_without_reprocessing:
            waste_and_feed_streams = None
            waste_streams = None
            extracted_mass = None
        else:
            for key in mats.keys():
                print('\nMass and volume of '
                      f'{key} before reproc: {mats[key].mass} g, ',
                      f'{mats[key].volume} cm3')
            waste_streams, extracted_mass = reprocess_materials(mats,
                                                                process_file,
                                                                dot_file)
            for key in mats.keys():
                print('\nMass and volume of '
                      f'{key} after reproc: {mats[key].mass} g, ',
                      f'{mats[key].volume} cm3')

            waste_and_feed_streams = refill_materials(mats,
                                                      extracted_mass,
                                                      waste_streams,
                                                      process_file)
            for key in mats.keys():
                print('\nMass and volume of '
                      f'{key} after refill: {mats[key].mass} g, ',
                      f'{mats[key].volume} cm3')

            print("Removed mass [g]:", extracted_mass)

         # Store in DB after reprocessing and refill (right before next depl)
        simulation.store_after_repr(mats, waste_and_feed_streams, step_idx)
        depcode.update_depletable_materials(mats, simulation.burn_time)

        # Preserve depletion and transport result and input files
        if not rebuild_saltproc_results:
            depcode.preserve_simulation_files(step_idx)

        del mats, waste_streams, waste_and_feed_streams, extracted_mass
        gc.collect()
        # Switch to another geometry?
        if simulation.adjust_geo and simulation.read_k_eds_delta(step_idx):
            depcode.switch_to_next_geometry()
        print("\nTime at the end of current depletion step: %fd" %
              simulation.burn_time)
        print("Simulation succeeded.\n")

def parse_arguments():
    """Parses arguments from command line.

    Parameters
    ----------

    Returns
    -------
    s : int
        Number of threads to use for shared-memory parallelism.
    i : str
        Path and name of main SaltProc input file (json format).

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--threads',
                        type=int,
                        default=None,
                        help='Number of threads to use for shared-memory \
                        parallelism.')
    parser.add_argument('-i',      # main input file
                        type=str,
                        default=None,
                        help='Path and name of SaltProc main input file')
    args = parser.parse_args()
    return args.threads, args.i


def read_main_input(main_inp_file):
    """Reads main SaltProc input file (json format).

    Parameters
    ----------
    main_inp_file : str
        Path to SaltProc main input file and name of this file.

    Returns
    -------
    input_path : Path
        Path to main input file
    process_file : str
        Path to the `.json` file describing the fuel reprocessing components.
    dot_file : str
        Path to the `.dot` describing the fuel reprocessing paths.
    mpi_args : list of str
        Arguments for running simulations on supercomputers using mpiexec or
        similar programs.
    rebuild_saltproc_results : bool
        Flag to indicate whether or not to rebuild SaltProc results file
        from existing depcode results
    run_without_reprocessing : bool
        Flag to indicate whether or not to run the depletion code in
        SaltProc without applying the reprocessing system.
    object_inputs : 3-tuple of dict
        tuple containing the inputs for constructing the
        :class:`~saltproc.Depcode`, :class:`~saltproc.Simulation`, and
        :class:`~saltproc.Reactor` objects.

    """

    input_schema = (Path(__file__).parents[0] / 'input_schema.json')
    with open(main_inp_file) as f:
        input_parameters = json.load(f)
        with open(input_schema) as s:
            schema = json.load(s)
            try:
                DefaultFillingValidator(schema).validate(input_parameters)
            except jsonschema.exceptions.ValidationError:
                print("Your input file is improperly structured: \n")
                traceback.print_exc()
            except jsonschema.exceptions.SchemaError:
                traceback.print_exc()
            except:
                print("Something went wrong during schema validation.")
                traceback.print_exc()

        # Global input path
        input_path = (Path.cwd() / Path(f.name).parents[0]).resolve()
        os.chdir(input_path)

        # Saltproc settings
        process_file = str((input_path /
                              input_parameters['proc_input_file']).resolve())
        dot_file = str((
            input_path /
            input_parameters['dot_input_file']).resolve())
        output_path = input_parameters['output_path']
        n_depletion_steps = input_parameters['n_depletion_steps']
        mpi_args = input_parameters['mpi_args']

        # Global output path
        output_path = (input_path / output_path)
        input_parameters['output_path'] = output_path.resolve()

        # Create output directoy if it doesn't exist
        if not Path(input_parameters['output_path']).exists():
            Path(input_parameters['output_path']).mkdir(parents=True)

        # Rebuild saltproc results?
        rebuild_saltproc_results = input_parameters['rebuild_saltproc_results']

        # Run without reprocessing?
        run_without_reprocessing = input_parameters['run_without_reprocessing']

        # Class settings
        depcode_input = input_parameters['depcode']
        simulation_input = input_parameters['simulation']
        reactor_input = input_parameters['reactor']

        codename = depcode_input['codename'].lower()
        if codename == 'serpent':
            depcode_input['template_input_file_path'] = str((
                input_path /
                depcode_input['template_input_file_path']).resolve())
        elif codename == 'openmc':
            for key in depcode_input['template_input_file_path']:
                value = depcode_input['template_input_file_path'][key]
                depcode_input['template_input_file_path'][key] = str((
                    input_path / value).resolve())
            depcode_input['chain_file_path'] = \
                str((input_path /
                 depcode_input['chain_file_path']).resolve())

            # process depletion_settings
            depletion_settings = depcode_input['depletion_settings']
            operator_kwargs = depletion_settings['operator_kwargs']
            if operator_kwargs != {}:
                fission_q_path = operator_kwargs['fission_q']
                if fission_q_path is not None:
                    operator_kwargs['fission_q'] = str(input_path / fission_q_path)
                depletion_settings['operator_kwargs'] = operator_kwargs
            depcode_input['depletion_settings'] = depletion_settings
        else:
            raise ValueError(f'{codename} is not a supported depletion code.'
                             ' Accepts: "serpent" or "openmc".')

        depcode_input['codename'] = codename
        depcode_input['output_path'] = output_path
        geo_list = depcode_input['geo_file_paths']

        # Global geometry file paths
        geo_file_paths = []
        for g in geo_list:
            geo_file_paths += [str((input_path / g).resolve())]
        depcode_input['geo_file_paths'] = geo_file_paths

        # Global output file paths
        db_name = (output_path / simulation_input['db_name'])
        simulation_input['db_name'] = str(db_name.resolve())

        reactor_input = _process_main_input_reactor_params(
            reactor_input, n_depletion_steps, depcode_input['codename'])

        return input_path, process_file, dot_file, mpi_args, rebuild_saltproc_results, run_without_reprocessing, (
            depcode_input, simulation_input, reactor_input)

def _print_simulation_input_info(simulation_input, depcode_input):
    """Helper function for `run()` """
    print('Initiating Saltproc:\n'
          '\tRestart = ' +
          str(simulation_input['restart_flag']) +
          '\n'
          '\tTemplate File Path  = ' +
          str(depcode_input['template_input_file_path']) +
          '\n'
          '\tOutput HDF5 database Path = ' +
          simulation_input['db_name'] +
          '\n')


def _create_depcode_object(depcode_input):
    """Helper function for `run()` """
    codename = depcode_input.pop('codename')
    depcode = CODENAME_MAP[codename]
    depcode = depcode(**depcode_input)
    depcode_input['codename'] = codename

    return depcode


def _create_simulation_object(simulation_input, depcode):
    """Helper function for `run()` """
    simulation = Simulation(
        sim_name='Super test',
        sim_depcode=depcode,
        restart_flag=simulation_input['restart_flag'],
        adjust_geo=simulation_input['adjust_geo'],
        db_path=simulation_input['db_name'])
    return simulation


def _create_reactor_object(reactor_input):
    """Helper function for `run()` """
    msr = Reactor(**reactor_input)
    return msr


def _process_main_input_reactor_params(reactor_input,
                                       n_depletion_steps,
                                       codename):
    """
    Process SaltProc reactor class input parameters based on the value and
    data type of the `n_depletion_steps` parameter as well as the depletion code
    being used, and throw errors if the input parameters are incorrect.
    """

    depletion_timesteps = np.array(reactor_input['depletion_timesteps'])
    power_levels = np.array(reactor_input['power_levels'])
    depletion_timesteps, power_levels = \
        _validate_depletion_timesteps_power_levels(n_depletion_steps,
                                                   depletion_timesteps,
                                                   power_levels)


    if reactor_input['timestep_type'] == 'cumulative':
        depletion_timesteps = _convert_cumulative_to_stepwise(depletion_timesteps)

    timestep_units = reactor_input['timestep_units']
    depletion_timesteps = _scale_depletion_timesteps(timestep_units,
                                                     depletion_timesteps,
                                                     codename)

    reactor_input['depletion_timesteps'] = depletion_timesteps.tolist()
    reactor_input['power_levels'] = power_levels.tolist()

    return reactor_input


def _validate_depletion_timesteps_power_levels(n_depletion_steps,
                                               depletion_timesteps,
                                               power_levels):
    """Ensure that the number of depletion timesteps and power levels match
    `n_depletion_steps` if it is given. Otherwise, compare the lengths of
    `depletion_timesteps` and `power_levels`"""
    if n_depletion_steps is not None:
        if n_depletion_steps < 0.0 or not int:
            raise ValueError('There must be a positive integer number'
                             ' of depletion steps. Provided'
                             f' n_depletion_steps: {n_depletion_steps}')
        if len(depletion_timesteps) == 1:
            depletion_timesteps = np.repeat(depletion_timesteps, n_depletion_steps)
        if len(power_levels) == 1:
            power_levels = np.repeat(power_levels, n_depletion_steps)

    if len(depletion_timesteps) != len(power_levels):
        raise ValueError('depletion_timesteps and power_levels length mismatch:'
                         f' depletion_timesteps has {len(depletion_timesteps)}'
                         f' entries and power_levels has {len(power_levels)}'
                         ' entries.')
    else:
        return depletion_timesteps, power_levels


def _convert_cumulative_to_stepwise(depletion_timesteps):
    ts = np.diff(depletion_timesteps)
    return np.concatenate(([depletion_timesteps[0]], ts))


def _scale_depletion_timesteps(timestep_units, depletion_timesteps, codename):
    """Scale `depletion_timesteps` to the correct value based on `timestep_units`"""
    # serpent base timestep units are days or mwd/kg
    if not(timestep_units in DAY_UNITS) and timestep_units.lower() != 'mwd/kg' and codename == 'serpent':
        if timestep_units in SECOND_UNITS:
            depletion_timesteps /= _SECONDS_PER_DAY
        elif timestep_units in MINUTE_UNITS:
            depletion_timesteps /= _MINUTES_PER_DAY
        elif timestep_units in HOUR_UNITS:
            depletion_timesteps /= _HOURS_PER_DAY
        elif timestep_units in YEAR_UNITS:
            depletion_timesteps *= _DAYS_PER_YEAR
        else:
            raise IOError(f'Unrecognized time unit: {timestep_units}')

    return depletion_timesteps

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

        if mat_name == material_for_extraction:
            for i, path in enumerate(extraction_process_paths):
                thru_flows[mat_name].append(initial_material)

                for proc in path:
                    # Calculate fraction of the flow going to the process proc
                    divisor = float(processes[proc].mass_flowrate /
                                    processes['core_outlet'].mass_flowrate)

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
    digraph = nx.drawing.nx_pydot.read_dot(dot_file)
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
        keys for feed streams that map to :class:`Materialflow` objects
        representing those material feed streams.

    """
    feeds = get_feeds(process_file)
    refill_mats = OrderedDict()
    # Get feed group for each material
    for mat, mat_feeds in feeds.items():
        # Get each feed in the feed group
        for feed_name, feed in mat_feeds.items():
            scale = extracted_mass[mat] / feed.mass
            refill_mats[mat] = scale * feed
            waste_streams[mat]['feed_' + str(feed_name)] = refill_mats[mat]
        mats[mat] += refill_mats[mat]
        print('Refilled fresh material: %s %f g' %
              (mat, refill_mats[mat].mass))
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
                comp = feed_data['comp']
                feeds[mat][feed_name] = Materialflow(comp=comp,
                                                     density=feed_data['density'],
                                                     volume=feed_data['volume'])
        return feeds
