.. _depcode_input:

``depcode`` Properties
======================

The ``depcode`` property has a large number of potential inputs depending on which depletion code we are using. The generic properties are given directly
below, and code-specific properties are given in their appropriate subsections.

.. note:: The code-specific properties add to or modify the existing generic
   properties. They do not replace them, but there can be new ones.

Generic properties
------------------

Required properties: ``codename``, ``template_input_file_path``, ``geo_file_paths``.

.. _codename_property:

``codename``
~~~~~~~~~~~~

  :description:
    Name of depletion code

  :type:
    ``string``

  :enum:
    ``serpent``, ``openmc``


.. _exec_path_property:

``exec_path``
~~~~~~~~~~~~~

  :description:
    Path to depletion code executable

  :type:
    ``string``


.. _template_input_file_path_property:

``template_input_file_path``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Path(s) to user's template depletion code input file(s) with reactor model


.. _geo_file_paths_property:

``geo_file_paths``
~~~~~~~~~~~~~~~~~~

  :description:
    Path(s) to geometry file(s) to switch to in depletion code runs

  :type:
    ``array``

  :items:
  
    :type:
      ``string``

    :minItems:
      1
   
    :uniqueItems:
      ``true``
            

.. _serpent_specific_properties:

Serpent-specific properties
---------------------------

.. _serpent_exec_path_property:

``exec_path``
~~~~~~~~~~~~~

  :default:
    ``sss2``
  

.. _serpent_template_input_file_path_property:

``template_input_file_path``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  :pattern: 
    ``^(.\\/)*(.*)$``
                  
``zaid_convention``
~~~~~~~~~~~~~~~~~~~

  :description:
    ZAID naming convention for nuclide codes. 'serpent': The third digit in ZA for nuclides in isomeric states is 3 (e.g. 47310 for for Ag-110m). 'mcnp': ZA = Z*1000 + A + (300 + 100*m). where m is the mth isomeric state (e.g. 47510 for Ag-110m). 'nndc': Identical to 'mcnp', except Am242m1 is 95242 and Am242 is 95642


  :type:
    ``string``

  :enum:
    "serpent", "mcnp", "nndc"

  :default:
    "mcnp"
 

.. _openmc_specific_properties:

OpenMC-specific properties
--------------------------

.. _openmc_exec_path_property:

``exec_path``
~~~~~~~~~~~~~

  :description:
    Path to OpenMC depletion script

  :const:
    ``openmc_deplete.py``

  :default:
    ``openmc_deplete.py``


.. _openmc_template_input_file_path_property:

``template_input_file_path``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Paths to OpenMC template input files.

  :type:
    ``object``.

  :required:
    ``settings``, ``materials``

  :properties:

    :settings:

      :description:
        OpenMC settings file

      :type:
        ``string``

      :pattern:
        ``^(.\\/)+(.+)\\.xml$``

      :default:
        ``settings.xml``

    :materials:

      :description:
        OpenMC materials file

      :type:
        ``string``

      :pattern:
        ``^(.\\/)*(.*)\\.xml$``

      :default:
        ``materials.xml``
    

.. _openmc_geo_file_paths_property:

``geo_file_paths``
~~~~~~~~~~~~~~~~~~

  :items:

    :type:
      ``string``

    :pattern:
      ``^(.\\/)*(.*)\\.xml$``

  :default:
    ``geometry.xml``


.. _openmc_chain_file_path_property:

``chain_file_path``
~~~~~~~~~~~~~~~~~~~

  :description:
    Path to depletion chain file

  :pattern:
    ``^(.\\/)*(.*)\\.xml$``

  :type:
    ``string``


.. _opemc_depletion_settings_property:

``depletion_settings``
~~~~~~~~~~~~~~~~~~~~~~
  :description:
    OpenMC depletion settings

  :type:
    ``object``.

  :default:
    ``{}``

  :properties:

    :method:

      :description:
        Integration method used for depletion

      :type:
        ``string``

      :enum:
        ``cecm``, ``predictor``, ``cf4``, ``epc_rk4``, ``si_celi``, ``si_leqi``,
        ``celi``, ``leqi``

      :default:
        ``predictor``
        

    :final_step:

      :description:
        Indicate whether or not a transport solve should be run at the end of the
        last timestep

      :type:
        ``boolean``

      :default:
        ``true``


    :operator_kwargs:

      :description:
        Keyword arguments passed to the depletion operator initalizer

      :type:
        ``object``

      :default:
        ``{}``

      :properties:
        :ref:`openmc_operator_kwargs_properties`
        
    :output:

      :description:
        Capture OpenMC output from standard out

      :type:
        ``boolean``

      :default:
        ``true``


    :integrator_kwargs:

      :description:
        Remaining keyword arguments for the depletion Integrator initalizer

      :type:
        ``object``

      :default:
        ``{}``

      :properties:

        :solver:

          :description:
            Bateman equations solver type

          :type:
            ``string``

          :enum:
            ``cram16``, ``cram48``


        :n_steps:

          :description:
            Number of stochastic iterations for stochastic integrators

          :type:
            ``number``

          :minimum:
            1


.. _openmc_operator_kwargs_properties:

``operator_kwargs`` Properties
------------------------------

``diff_burnable_mats``
~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Whether to differentiate burnable materials with multiple instances.

  :type:
    ``boolean``

  :default:
    ``false``


``normalization_mode``
~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Indicate how tally resutls should be normalized

  :type:
    ``string``

  :enum:
    ``energy-deposition``, ``fission-q``, ``source-rate``

  :default:
    ``fission-q``


``fission_q``
~~~~~~~~~~~~~

  :description:
    Path to fission Q values

  :default:
    ``null``


``dilute_initial``
~~~~~~~~~~~~~~~~~~

  :description:
    Initial atom density to add for nuclides that are zero in initial
    condition.

  :type:
    ``number``

  :minimum:
    0

  :default:
    1000


``fission_yield_mode``
~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Determine what fission energy helper is used

  :type:
    ``string``

  :enum:
    ``constant``, ``cutoff``, ``average``

  :default:
    ``constant``


``fission_yield_opts``
~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Arguments for the fission yield helper

  :default:
    ``null``. See :ref:`openmc_constant_fission_yield_opts_properties`
    and :ref:`openmc_cutoff_fission_yield_opts_properties` for object
    properties when ``fission_yield_mode`` is ``constant`` and
    ``cutoff``, respectively.


``reaction_rate_mode``
~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Indicate how one-group reaction rates should be calculated

  :type:
    ``string``

  :enum:
    ``direct``, ``flux``

  :default:
    ``direct``


``reaction_rate_opts``
~~~~~~~~~~~~~~~~~~~~~~

  :default:
    ``null``. See :ref:`openmc_flux_reaction_rate_opts_properties` for
    object properties when ``reaction_rate_mode`` is ``flux``.


``reduce_chain``
~~~~~~~~~~~~~~~~

  :description:
    Whether or not to reduce the depletion chain.

  :type:
    ``boolean``

  :default:
    ``false``


``reduce_chain_level``
~~~~~~~~~~~~~~~~~~~~~~

  :description:
    Depth of serach while reducing depletion chain

  :default:
    ``null``


.. _openmc_constant_fission_yield_opts_properties:

``fission_yield_opts`` Properties -- ``constant`` fission yield mode
--------------------------------------------------------------------

``energy``
~~~~~~~~~~

  :description:
    Energy of fission yield libraries [MeV]

  :type:
    ``number``


.. _openmc_cutoff_fission_yield_opts_properties:

``fission_yield_opts`` Properties -- ``cutoff`` fission yield mode
------------------------------------------------------------------

``cutoff``
~~~~~~~~~~

  :description:
    Cutoff energy in eV

  :type:
    ``number``


``thermal_energy``
~~~~~~~~~~~~~~~~~~

  :description:
    Energy of yield data corresponding to thermal yields

  :type:
    ``number``

    
``fast_energy``
~~~~~~~~~~~~~~~

  :description:
    Energy of yield data corresponding to fast yields

  :type:
    ``number``


.. _openmc_flux_reaction_rate_opts_properties:

``reaction_rate_opts`` Properties -- ``flux`` reaction rate mode
----------------------------------------------------------------

``energies``
~~~~~~~~~~~~

  :description:
    Energy group boundaries

  :type:
    ``array``

  :items:
    
    :type:
      ``number``

    :minItems:
      2


``reactions``
~~~~~~~~~~~~~

  :description:
    Reactions to tally

  :type:
    ``array``

  :items:

    :type:
      ``string``

    :minItems:
      1


``nuclides``
~~~~~~~~~~~~

  :description:
    Nuclides on which to tally reactions

  :type:
    ``array``

  :items:

    :type:
      ``string``

    :minItems:
      1
