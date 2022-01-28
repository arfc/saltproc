Overview
=========

SaltProc couples directly with the Monte Carlo neutron transport code Serpent 2
and enables sophisticated, multi-component online fuel reprocessing system
modeling. SaltProc is the first open-source tool for liquid-fueled MSR
depletion simulation with the following capabilities:

- neutron poison removal with user-defined efficiency,
- make-up mass loss by fresh fuel injection,
- reactivity control by adjusting fuel feed rate or geometry change,
- can model any reactor design,
- potentially, can couple with any depletion tool (i.e., MCNP, SCALE, OpenMC).


How SaltProc works
-------------------

SaltProc is a driver for Serpent to simulate online fuel salt reprocessing for
Molten Salt Reactors. It performs following major functions:

  - runs SERPENT
  - parses and stores Serpent output data in HDF5
  - modifies parsed material composition (`reprocesses`)
  - creates Serpent input file


The code logic flow is the following:

  1. Runs Serpent (`saltproc.depcode.run_depcode()`)
  2. Parses through the output `*_dep.m` file and creates PyNE Material object
     for each burnable material.
  3. Processes Fuel (`saltproc.app.reprocessing()` and `saltproc.refill`):

    * Passes fuel composition throughout Processes objects (reprocessing system
      components) to remove poisons with specific efficiency.
    * Adds back fissile and/or fertile material to make-up loss of material.

  4. Records data:

    - Depleted fuel composition (`materials/fuel/before_reproc` table in HDF5)
    - Reprocessed fuel composition (`materials/fuel/after_reproc` table in
      HDF5)
    - Multiplication factor at the beginning and at the end of depletion step
      (`simulation_parameters/keff_bds`, `simulation_parameters/keff_eds`)
    - Effective Delayed Neutron Fraction (:math:`\beta_{eff}`) at the end of
      the depletion step (`simulation_parameters/beta_eff_eds`)
    - Waste and feed streams from each `Process` (`materials/in_out_streams/`)

  5. Repeats 1-4.

Updates
-------

March 2021:

Besides the existing flexibility like fixed removal efficiency definition for
each target isotope defined in the object input file, Saltproc code now
comprises `Sparging System package` that calculates removal efficiencies for
various target isotopes (i.e., Xe, Kr, and H). To enable this feature, use
the `"self"` command in the input file in the `"efficiency"` object names of
Sparger and Separator components. Each component can be employed separately.
An example is given below. In the example, capacity and mass flow rate are in
`g/s` unit while volume is in `cm`:math:`^3` unit.

"sparger": { "capacity": 9920000,
			 "efficiency": "self",
			 "mass_flowrate": 9920000,
			 "volume": 10000000 },
"entrainment_separator": { "capacity": 9920000,
						   "efficiency": "self",
						   "mass_flowrate": 9920000,
						   "volume": 11 }

The Future
-----------

A number of features will be implemented in SaltProc soon. Support of various
depletion codes (e.g., OpenMC) will be added.


.. warning::

    SaltProc is a relatively new project and is still under heavy development.
    Although we will make our best effort to maintain compatibility with the
    current API, inevitably the API will change in future versions as SaltProc
    matures.
