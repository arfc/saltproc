.. _saltproc_overview:

Overview
=========

SaltProc couples directly with a variety of neutron transport codes with
depletion capabilities and enables sophisticated, multi-component online fuel
reprocessing system modeling. SaltProc is the first open-source tool for
liquid-fueled depletion simulations with the following capabilities:

  - Neutron poison removal with user-defined efficiency,

  - Make-up mass loss by fresh fuel injection,

  - Reactivity control by adjusting fuel feed rate or reactor geometry (i.e. control rod depth),

  - Can model any reactor design,
  
  - Couples with OpenMC and SERPENT (and extendable to other tools such as MCNP or SCALE). 
.. _supported_codes:

Currently supported transport solvers:

  - `Serpent2`_

  - `OpenMC`_

.. _Serpent2: http://montecarlo.vtt.fi
.. _OpenMC: https://openmc.org/


How SaltProc works
-------------------

SaltProc is a driver for Monte Carlo transport codes with depletion capabilities (henceforth referred to as *transport-depletion codes*) to simulate online fuel salt reprocessing for
Molten Salt Reactors. It performs following major functions:

  - Runs the transport-depletion code
  - Parses and stores depleted material data in HDF5
  - Modifies parsed material composition (`reprocesses`)
  - Creates a new transport-depletion code input file


The code logic flow is the following:

  1. Runs the transport-depletion code (:meth:`saltproc.depcode.Depcode.run_depcode()`)
  2. Parses through the output `*_dep.m` file and creates PyNE Material object
     for each burnable material.
  3. Processes Fuel (:meth:`saltproc.app.reprocess_materials()` and :meth:`saltproc.app.refill_materials()`):

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
----------

.. _issues page on GitHub: https://github.com/arfc/saltproc/issues

A number of features will be implemented in SaltProc soon. Take a look at the 
`issues page on GitHub`_ to see what we are working on.

.. warning::

    SaltProc is a relatively new project and is still under heavy development.
    Although we will make our best effort to maintain compatibility with the
    current API, inevitably the API will change in future versions as SaltProc
    matures.
