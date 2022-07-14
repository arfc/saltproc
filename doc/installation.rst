Installation
============

SaltProc has the following dependencies:

  #. `Python`_ (>=3.5)
  #. `Serpent`_ (>=2.1.31)
  #. `PyNE`_ (>=0.5.11)
  #. `OpenMC`_ (>=0.13.0)
  #. `NumPy`_ (>=1.14.0)
  #. `PyTables`_
  #. `NetworkX`_
  #. `PyDotPlus`_
  #. `jsonschema`_

.. _Serpent: http://montecarlo.vtt.fi
.. _PyNE: http://pyne.io
.. _OpenMC: https://openmc.org/
.. _Python: http://python.org
.. _NumPy: http://numpy.org
.. _PyTables: http://pytables.org
.. _NetworkX: http://networkx.github.io
.. _PyDotPlus: https://pydotplus.readthedocs.io/
.. _pytest: https://docs.pytest.org
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
  #. `ViTables`_



Clone the source from the SaltProc repository from `GitHub`_.

.. code-block:: bash

   git clone git@github.com:arfc/saltproc.git

Note on installing OpenMC
-------------------------
The ``conda-forge`` build of OpenMC 0.13.0 cannot be installed alongside the ``conda-forge`` build of PyNE due to a conflict in the pinned HDF5 versions required by those builds. Since both are dependencies, users will need to pick one to install from source. We recommend users install OpenMC from source as it has a more active community and a step-by-step guide on how to install it from source on most machines. For Ubuntu users, consider using the `ubuntu-nuclear-software-installer`_
script to install OpenMC from source.

.. _ubuntu-nuclear-software-installer: https://github.com/yardasol/ubuntu-nuclear-software-installer

Otherwise, all of the dependencies are readily available through the `conda package manager`_.

.. note:: We recommend using the `mamba`_ CLI tool to install packages quickly. SaltProc has a compltex package dependency structure which can result is long environment solve times in the default ``conda`` solver. ``mamba`` is a reimplementation of ``conda`` in ``C++`` and we have found it is significantly faster.

You can download the required ones using ``conda`` on the provided ``environment.yml``
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
The ``DepcodeSerpent`` integration tests require the `JEFF 3.1.2 cross section library`_ as well
as neutron induces and spontaneous fission product yield data from JEFF 3.3. 
The publicly available versions of JEFF 3.1.2 cannot be used with Serpent right
out of the box due to `Serpent's notation for isomeric states`_. The scripts in
``scripts/xsdata`` download all necessary libraries and perform all the necessary processing on them for use in Serpent 2.
We recommend using them for your convenience. 
See the `README`_ for more information.

..
  The ``DepcodeOpenmc`` integration tests require...

.. _Serpent's notation for isomeric states: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries
.. _JEFF 3.1.2 cross section library: https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/JEFF312/
.. _README: https://github.com/arfc/saltproc/blob/master/scripts/README.md

To run the tests, execute:

.. code-block:: bash

   pytest saltproc/

from the root directory of SaltProc. If you just want to run the unit tests, execute

.. code-block:: bash

   pytest --ignore saltproc/tests/integration_tests saltproc/

