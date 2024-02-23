.. _simulation_input:

``simulation`` Properties
=========================

Required properties: ``sim_name``, ``db_name``

.. _sim_name_property:

``sim_name``
------------

  :description:
    Name of simulation

  :type:
    ``string``


.. _db_name_property:

``db_name``
-----------

  :description:
    Output HDF5 database file name

  :type:
    ``string``

  :default:
    ``saltproc_results.h5``

  :pattern:
    ``^(.*)\\.h5$``


.. _restart_flag_property:

``restart_flag``
----------------

  :description:
    Restart simulation from the step when it stopped?

  :type:
    ``boolean``

  :default:
    ``false``


.. _adjust_geo_property:

``adjust_geo``
--------------

  :description:
    switch to another geometry when keff drops below 1?

  :type:
    ``boolean``

  :default:
    ``false``
