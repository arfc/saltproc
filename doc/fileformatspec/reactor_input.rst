.. _reactor_input:

``reactor`` Properties
=========================

Required properties: ``volume``, ``mass_flowrate``, ``power_levels``,
``depletion_timesteps``, ``timestep_units``

.. _volume_property:

``volume``
----------
  :description:
    reactor core volume [cm^3]

  :type:
    ``number``

  :minimum:
    0


.. _mass_flowrate_property:

``mass_flowrate``
-----------------

  :description:
    Salt mass flowrate through reactor core [g/s]

  :type:
    ``number``

  :minimum:
    0


.. _power_levels_property:

``power_levels``
----------------

  :description:
    Reactor power or power step list durng depletion step [W]

  :type:
    ``array``

  :items:
    
    :type:
      ``number``
    
    :minimum:
      0

  :minItems:
    1

  :uniqueItems:
    ``false``


.. _depletion_timesteps_property:

``depletion_timesteps``
-----------------------

  :description:
    Depletion step length(s)

  :type:
    ``array``

  :items:

    :type:
      ``number``
    
    :minimum:
      0

  :minItems:
    1

  :uniqueItems:
    ``false``

.. _timestep_type_property:

``timestep_type``
-----------------

  :description:
    Depletion step type

  :type:
    ``string``

  :enum:
    ``cumulative``, ``stepwise``

  :default:
    ``stepwise``

.. _timestep_unites_property:

``timestep_units``
------------------

  :description:
    Timestep unit

  :type:
    ``string``

  :enum:
    ``s``, ``sec``, ``min``, ``minute``, ``h``, ``hr``, ``hour``, ``d``, ``day``, ``a``, ``year``, ``MWd/kg``, ``mwd/kg``, ``MWD/KG``, ``MWD/kg``, ``MWd/KG``
