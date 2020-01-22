Overview
=========

SaltProc couples directly with the Monte Carlo neutron transport Serpent 2 and
enables sophisticated, multi-component online fuel reprocessing system modeling.
SaltProc is the first open-source tool for liquid-fueled MSR depletion
simulation with following capabilities:

- neutron poison removal with user-defined efficiency,
- make-up mass loss by fresh fuel injection,
- reactivity control by adjusting fuel feed rate or geometry change,
- for any reactor design,
- potentially, can couple with any depletion tool (i.e., MCNP, SCALE, OpenMC).


How SaltProc works
---------

SaltProc is a driver for Serpent to simulate online fuel salt reprocessing for
Molten Salt Reactors. It performs three major functions:

  - runs SERPENT
  - parses and stores Serpent output data in HDF5
  - modifies parsed material composition (`reprocesses`)
  - creates Serpent input file


The code logic flow is the following:
^^^^^^^^^^^^^^^^^^^^^^^^^^^
  1. Runs Serpent (`saltproc.depcode.run_depcode()``)
  2. Parses through the output *_dep.m file and create PyNE Material object for each burnable material.
  3. Processes Fuel (`saltproc.app.reprocessing()` and `saltproc.refill`):
    * Passes fuel composition throughout Processes objects (reprocessing system components) to remove poisons with specific efficiency.
    * Add back fissile and/or fertile material to make-up loss of material.
  4. Records data:
    - Depleted fuel composition (`materials/fuel/before_reproc` table in HDF5)
    - Reprocessed fuel composition (`materials/fuel/after_reproc` table in HDF5)
    - Multiplication factor at the beginning and at the end of depletion step (`simulation_parameters/keff_bds`, `simulation_parameters/keff_eds`)
    - Effective Delayed Neutron Fraction (:math:`\beta_{eff}`) at the end of the depletion step (`simulation_parameters/beta_eff_eds`)
    - Waste and feed streams from each `Process` (`materials/in_out_streams/`)
  5. Repeat 1-4.


The Future
-----------

Number of features will be implemented in SaltProc soon. Support of various
depletion codes (e.g., OpenMC) will be added.


.. warning::

    SaltProc is a relatively new project and is still under heavy development.
    Although we will make a best effort to maintain compatibility with the
    current API, inevitably the API will change in future versions as SaltProc
    matures.
