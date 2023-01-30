.. _saltproc_input:

SaltProc Input File
===================

The main SaltProc input file is a JSON file validated against a JSON schema.
In this section, we will describe the structure of this schema. The top level
datatype of the schema is a JSON ``object``.

Required properties are as follows: ``proc_input_file``, ``dot_input_file``, ``output_path``, ``depcode``, ``simulation``, ``reactor``.

.. _proc_input_file_property:

``proc_input_file``
-------------------

  :description:
    File containing processing system objects

  :type: 
    ``string``
            
  :pattern:
    ``^(.*)\\.json$``
        

.. _dot_input_file_property:

``dot_input_file``
------------------

  :description: 
    Graph file containing processing system structure

  :type:
    ``string``

  :pattern:
    ``^(.*)\\.dot$``


.. _output_path_property:

``output_path``
---------------

  :description:
    Path output data storing folder
    
  :type:
    ``string``

  :pattern:
    ``^(.\\/)*(.*)$``

  :default:
    ``saltproc_runtime``


.. _n_depletion_steps_property:

``n_depletion_steps``
---------------------

  :description:
    Number of steps for constant power and depletion interval case

  :type:
    ``number``


.. _mpi_args_property:

``mpi_args``
---------------------

  :description:
    Arguments for running simulations on supercomputers using ``mpiexec``
    or similar programs

  :type:
    ``array``, ``null``

  :items:

    :type:
      ``string``, ``integer``

  :default:
    ``null``


.. _depcode_property:

``depcode``
-----------

  :description:
    Depcode class input parameters

  :type:
    ``object``

  :default:
    ``{}``

  :properties:
    :ref:`depcode_input`

.. _simulation_property:

``simulation``
--------------

  :description:
    Simulation class input parameters

  :type:
    ``object``

  :default:
    ``{}``

  :properties:
    :ref:`simulation_input`

.. _reactor_property:

``reactor``
-----------

  :description:
    Reactor class input parameters

  :type:
    ``object``. See :ref:`reactor_input` for object properties.

  :default:
    ``{}``

  :properties:
    :ref:`reactor_input`
