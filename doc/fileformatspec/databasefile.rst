================
HDF5 Output File
================
This file format specification uses the pytables terminology.

:Leaves:

**/inital_depcode_siminfo** -- (*Table*) - Table has the shape (1,)
  - Column 0: **neutron_population** -- (*int*) - 
  - Column 1: **active_cycles** -- (*int*) - 
  - Column 2: **inactive_cycles** -- (*int*)  - 
  - Column 3: **depcode_name** -- (*str*) - 
  - Column 4: **depcode_version** -- (*str*) - 
  - Column 5: **title** -- (*str*) - 
  - Column 6: **depcode_input_filename** -- (*str*) - 
  - Column 7: **depcode_working_dir** -- (*str*) - 
  - Column 8: **xs_data_path** -- (*str*) - 
  - Column 9: **OMP_threads** -- (*int*) - 
  - Column 10: **MPI_Tasks** -- (*int*) - 
  - Column 11: **memory_optimization_mode** -- (*int*) - 
  - Column 12: **depletion_timestep** -- (*int*) - 


**/simulation_parameters** -- (*Table*) - Table has the shape (number of timesteps,)
  - Column 0: **beta_eff_eds** -- (*float[][2]*) -  The array has the shape (number of delayed groups, 2)
  - Column 1: **breeding_ratio** -- (*float[2]*) - 
  - Column 2: **cumulative_time_at_eds** -- (*int*) - 
  - Column 3: **delayed_neutrons_lambda_eds** -- (*float[][2]*) - The array has the shape (number of delayed groups, 2)
  - Column 4: **fission_mass_bds** -- (*float*) - 
  - Column 5: **fission_mass_eds** -- (*float*) - 
  - Column 6: **keff_bds** -- (*float[2]*) - 
  - Column 7: **keff_eds** -- (*float[2]*) - 
  - Column 8: **memory_usage** -- (*float*) - 
  - Column 9: **power_level** -- (*float*) - 
  - Column 10: **step_execution_time** -- (*float*) - 
   

**/materials/<fuel/ctrlPois>/<before/after>_reproc/parameters** -- (*Table*) - Table has the shape (<1/0> + number of timesteps, 7)
  - Column 0: **mass** -- (*float*) - 
  - Column 1: **density** -- (*float*) - 
  - Column 2: **volume** -- (*float*) - 
  - Column 3: **temperature** -- (*float*) - 
  - Column 4: **mass_flowrate** -- (*float*) - 
  - Column 5: **void_fraction** -- (*float*) - 
  - Column 6: **burnup** -- (*float*) - 

**/materials/<fuel/ctrlPois>/<before/after>_reproc/comp** -- (*float[][]*) - wt-percent composition of nuclides in the fuel. The array has the shape (<1/0> + number of timesteps, number of nuclides)


**/materials/<fuel/ctrlPois>/in_out_streams/<stream name>** -- (*float[][]*) - The array has the shape (number of timesteps, number of nuclides in stream)

