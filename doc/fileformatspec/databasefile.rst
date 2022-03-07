================
HDF5 Output File
================
This file format specification uses the pytables terminology.

**/**

:Leaves: - **inital_depcode_siminfo** -- (*Table*)
         - **simulation_parameters** -- (*Table*)
   
**/materials/<fuel/ctrlPois>/<before/after>_reproc/**

:Leaves: - **parameters** ()
         - **comp** (*double[][]*) -- wt-percent composition of nuclides in the fuel. The array has the shape (number of timesteps, number of nuclides)


**/materials/<fuel/ctrlPois>/in_out_streams/**

:Leaves: - **<stream name>** ()
