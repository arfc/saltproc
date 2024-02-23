Installation
============

SaltProc has the following dependencies:

  #. `python`_ (>=3.5)
  #. `serpent`_ (>=2.1.31)
  #. `serpentTools`_
  #. `openmc`_ (>=0.13.0)
  #. `numpy`_ (>=1.14.0)
  #. `PyTables`_
  #. `networkx`_
  #. `pydot`_
  #. `jsonschema`_

.. _serpent: http://montecarlo.vtt.fi
.. _serpentTools: https://serpent-tools.readthedocs.io/en/master/index.html
.. _openmc: https://openmc.org/
.. _python: http://python.org
.. _numpy: http://numpy.org
.. _PyTables: http://pytables.org
.. _networkx: http://networkx.github.io
.. _pydot: https://github.com/pydot/pydot
.. _pytest: https://docs.pytest.org
.. _pytest documentation: https://docs.pytest.org/en/latest/how-to/usage.html
.. _sphinx: https://www.sphinx-doc.org
.. _sphinx-rtd-theme: https://sphinx-rtd-theme.readthedocs.io
.. _matplotlib: http://matplotlib.org
.. _ViTables: http://vitables.org
.. _GitHub: http://github.com/arfc/saltproc
.. _jsonschema: https://github.com/Julian/jsonschema
.. _conda package manager: https://docs.conda.io/en/latest/
.. _mamba: https://github.com/mamba-org/mamba

Optional Dependencies:
  #. `pytest`_ (for testing)
  #. `sphinx`_ and `sphinx-rtd-theme`_ (for building documentation)
  #. `matplotlib`_



Clone the source from the SaltProc repository from `GitHub`_.

.. code-block:: bash

   git clone git@github.com:arfc/saltproc.git

.. note:: We recommend using the `mamba`_ CLI tool to install packages quickly. SaltProc has a compltex package dependency structure which can result is long environment solve times in the default ``conda`` solver. ``mamba`` is a reimplementation of ``conda`` in ``C++`` and we have found it is significantly faster.

You can download the required packages using ``conda`` on the provided ``environment.yml``
file in the repository:

.. code-block:: bash
    
   cd saltproc/
   conda env create -f environment.yml

Once all the dependencies are installed, SaltProc can be installed by
running the following commands from within the cloned directory
repository (assuming the `saltproc-env` environment is active):

.. code-block:: bash

   pip install .

Please let us know if you run into trouble.


Cross Section Configuration
---------------------------
SaltProc can use any cross section library that its depletion codes can. Currently supported depletion codes and their guides on cross section configuration are listed below:

  - Serpent: See `this page on the Serpent wiki`_ for information on how to configure the libraries. 
  - OpenMC: See `this page on the OpenMC docs`_ for information on how to configure the libraries. You can also convert a Serpent cross section library to an OpenMC cross section library using `their included scripts`_.

.. _this page on the Serpent wiki: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries
.. _this page on the OpenMC docs: https://docs.openmc.org/en/stable/usersguide/cross_sections.html
.. _their included scripts: https://docs.openmc.org/en/stable/usersguide/scripts.html#openmc-ace-to-hdf5


Testing
-------
The SaltProc test suite has two types of tests: unit tests and regression tests.
The unit tests check that the individual functions and classes of the ``saltproc``
module return the correct type of variables and correct values, where applicable. 
The regression tests run a full SaltProc simulation and check the final result
with a precalculated result. 
The ``SerpentDepcode`` integration tests require the `JEFF 3.1.2 cross section library`_ as well
as neutron induces and spontaneous fission product yield data from JEFF 3.3. 
The publicly available versions of JEFF 3.1.2 cannot be used with Serpent right
out of the box due to `Serpent's notation for isomeric states`_. The scripts in
``scripts/xsdata`` download all necessary libraries and perform all the necessary processing on them for use in Serpent 2.
We recommend using them for your convenience. 
See the `README`_ for more information.

..
  The ``OpenMCDepcode`` integration tests require...

.. _Serpent's notation for isomeric states: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries
.. _JEFF 3.1.2 cross section library: https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/JEFF312/
.. _README: https://github.com/arfc/saltproc/blob/master/scripts/README.md

To run the tests, execute:

.. code-block:: bash

   pytest test/

from the root directory of SaltProc. If you want to just the unit tests,
execute:

.. code-block:: bash

   pytest tests/unit_tests

Similarly, for just the integration tests, execute:

.. code-block:: bash

   pytest tests/integration_tests

For more precise control, please refer to the `pytest documentation`_.
