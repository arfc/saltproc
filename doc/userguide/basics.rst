.. _userguide_basics:

Basics of Using SaltProc
========================

Running a Model
---------------
SaltProc is built in Python, so rather than calling an executable to run
SaltProc, you call Python and invoke the SaltProc module. You use the ``-i``
flag to specify a path to the :ref:`saltproc_input`:

.. code-block:: bash

   python -m saltproc -i saltproc_input.json

The first thing SaltProc does when running a simulation is read this input file
and validate that it is correct. At a minium, the input file requires six
parameters to be filled by the user:

.. admonition:: Required
   :class: error
   
   :ref:`proc_input_file_property`
     This file describes the properties of each processing system component.

   :ref:`dot_input_file_property`
     This file describes the strucutre of the processing system as a graph

   :ref:`n_depletion_steps_property`
     Specifies the number of depletion steps to run.

   :ref:`depcode_property`
     This parameter contains runtime options for the transport code as a
     dictionary. The parameters expected change depending on which transport
     code is used, but at a minimum there will be parameters to specify
     geometry and material files for all transport codes. See
     :ref:`depcode_input` for a full listing of these options.

   :ref:`simulation_property`
     This parameter contains the name of the simulation, as well as
     options to restart the simulation from when it stopped (in the 
     case of a runtime error), as well as an option to turn on geometry
     switching. See :ref:`simulation_input` for a full listing of these
     options

   :ref:`reactor_property`
     This parameter contains setttings for the depletion simulation
     (number of timesteps, power level, timestep units). See
     :ref:`reactor_input` for a full listing of these options.

.. admonition:: Optional
   :class: note

   :ref:`mpi_args_property`
     Users running a simulation on a computer with multiple cores, sockets, or
     nodes will benefit from utilizing all available hardware resources on the
     transport simulation. This parameter holds commands to execute a simulation
     using MPI for distribtued memory parallelism. Note that the user must include
     the executable in this parameter (``mpiexec``, ``mpirun``, etc.). We discuss
     this in greater detail in :ref:`userguide_parallel`.

JavaScript Object Notation (JSON)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SaltProc uses :ref:`JSON` to structure its input files. JSON is used as it has
all the capabilities of stuctured markup language like :ref:`XML`, but intead
of using tags, it is structured more or less like a dictionary data structure.
This has the benefit of being extremely easy and quick to write by hand.

.. _JSON: https://www.json.org/json-en.html
.. _XML: https://www.w3.org/XML/

Creating input files
~~~~~~~~~~~~~~~~~~~~
SaltProc input files are written by hand. We cover how to do this in detail
in the next section of the User Guide.

.. note::
   The majority of work preparing
   for a SaltProc simulation is not writing the SaltProc input file, but
   creating the model for the transport code. The steps and syntax for
   this vary from code to code. See
   :ref:`the list of supported codes <supported_codes>` for links to
   documentation.

Viewing and Analyzing Results
-----------------------------
After a simulation is completed by running ``saltproc``, all of the transport
code results and input files are stored in the ``saltproc_runtime`` directory
(unless you provided a path for :ref:`output_path_property` in the input file,
in which case the results are stored in a directory with that path):

``saltproc_results.h5``
  An HDF5 file containing material compositions for all depletable materials,
  including compositions before and after reprocessing, as well as delayed
  neutron data. See :ref:`results_file` for a full listing of parameters.

``step_i_data``
  A directory storing input and output files for the transport simulation(s)
  for the :math:`i`-th depletion step.

.. note:: 
   Users must use :ref:`PyTables` to load and read results directly from
   the HDF5 file. An API for doing this is in development.

Physical Units
--------------
SaltProc results use the following units unless otherwise specified.

======= ============ ======
Measure Default unit Symbol
======= ============ ======
mass    kilogram     kg
power   watt         W
time    days         d
======= ============ ======

