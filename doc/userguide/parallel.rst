.. _userguide_parallel:

Running in Parallel
===================

If you have installed your :ref:`supported depletion code <supported_codes>`
with support for shared or distributed memory parallelism (typically via OpenMP
or MPI, respectively) support, then you can take advantage of that parallelism
in SaltProc as well. 

.. _parallel_shared:

Shared-Memory Parallelsim
----------------------------------

To specify the number of theads to use in shared memory parallelism, use the
`-s` or `--threads` command line argument when calling SaltProc. Note that
this argument currently does not affect how OpenMC uses shared-memory
parallelsim, as there is no way to specify the number of threads used
in depletion. The default behavior is to use all available threads.
User's should read more about this
`here <https://docs.openmc.org/en/stable/usersguide/parallel.html#shared-memory-parallelism-openmp>`_.

.. _parallel_distributed:

Distributed-Memory Parallelism
------------------------------

SaltProc provides the :ref:`mpi_args_property` parameter in the input file to
give users flexible access to programs like ``mpiexec``. ``mpi_args`` is a list
of strings that is appended to the subprocess call for each depletion step.

For example, if we are using ``mpiexec``, and want to do a distributed-memory run on
two nodes, then in our input file, we should have the following parameter:

.. code-block:: json

  "mpi_args": ["mpiexec", "-n", "2"]
