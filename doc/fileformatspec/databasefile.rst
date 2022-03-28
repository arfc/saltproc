================
HDF5 Output File
================
This file format specification uses the pytables terminology.

:Leaves:

**/inital_depcode_siminfo** -- (*Table*) - Table has the shape (1,)
  - Column 0: **neutron_population** -- (*int*) - Number of particles
  - Column 1: **active_cycles** -- (*int*) - Number of active cycles/batches 
  - Column 2: **inactive_cycles** -- (*int*)  - Number of inactive cycles/batches
  - Column 3: **depcode_name** -- (*str*) - Name of depletion code
  - Column 4: **depcode_version** -- (*str*) - Depletion code version number
  - Column 5: **title** -- (*str*) - Simulation title
  - Column 6: **depcode_input_filename** -- (*str*) - Input filename for depletion code
  - Column 7: **depcode_working_dir** -- (*str*) - Directory where results are stored
  - Column 8: **xs_data_path** -- (*str*) - Path to cross section library
  - Column 9: **OMP_threads** -- (*int*) - Number of OMP threads assigned
  - Column 10: **MPI_Tasks** -- (*int*) - Number of MPI tasks assigned
  - Column 11: **memory_optimization_mode** -- (*int*) - Serpent memory optimization mode
  - Column 12: **depletion_timestep** -- (*int*) - Size of depletion timestep


**/simulation_parameters** -- (*Table*) - Table has the shape (number of timesteps,)
  - Column 0: **beta_eff_eds** -- (*float[][2]*) - Delayed neutron fractions. The array has the shape (number of delayed groups, 2)
  - Column 1: **breeding_ratio** -- (*float[2]*) - Breeding ratio in the fuel.
  - Column 2: **cumulative_time_at_eds** -- (*int*) - Cumulative time at end of depletion step [days]
  - Column 3: **delayed_neutrons_lambda** -- (*float[][2]*) - Delayed neutron precursor decay constants. The array has the shape (number of delayed groups, 2)
  - Column 4: **fission_mass_bds** -- (*float*) - Fissile mass at beginning of depletion step [kg]
  - Column 5: **fission_mass_eds** -- (*float*) - Fissile mass at end of depletion step [kg]
  - Column 6: **keff_bds** -- (*float[2]*) - k_eff at beginning of depletion step
  - Column 7: **keff_eds** -- (*float[2]*) - k_eff at end of depletion step
  - Column 8: **memory_usage** -- (*float*) - Memory used in depletio step [MB]
  - Column 9: **power_level** -- (*float*) - Neutron fission power [W]
  - Column 10: **step_execution_time** -- (*float*) - Depletion step running time [minutes]
   

**/materials/<fuel/ctrlPois>/<before/after>_reproc/parameters** -- (*Table*) - Material parameters. Table has the shape (<1/0> + number of timesteps, 7)
  - Column 0: **mass** -- (*float*) - Mass of material [g]
  - Column 1: **density** -- (*float*) - Mass density of material [g/cm^3]
  - Column 2: **volume** -- (*float*) - Volume of material [cm^3]
  - Column 3: **temperature** -- (*float*) - Material temperature [K]
  - Column 4: **mass_flowrate** -- (*float*) - Mass flowrate of material [g/s]
  - Column 5: **void_fraction** -- (*float*) - Void fraction in material [%]
  - Column 6: **burnup** -- (*float*) - Material burnup at end of depletion step [MWd/kgU]

**/materials/(fuel,ctrlPois)/(before,after)_reproc/comp** -- (*float[][]*) - wt-percent composition of nuclides in the fuel or control poison. The array has the shape (<1/0> + number of timesteps, number of nuclides)


**/materials/(fuel,ctrlPois)/in_out_streams/<stream name>** -- (*float[][]*) - wt-percent composition of nuclides in the material stream. The array has the shape (number of timesteps, number of nuclides in stream)

