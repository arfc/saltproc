Installation
============

SaltProc has the following dependencies:

  #. `Python`_ (>=3.5)
  #. `Serpent`_ (>=2.1.31)
  #. `PyNE`_ (>=0.5.11)
  #. `NumPy`_ (>=1.14.0)
  #. `PyTables`_
  #. `NetworkX`_
  #. `PyDotPlus`_

.. _Serpent: http://montecarlo.vtt.fi
.. _PyNE: http://pyne.io
.. _Python: http://python.org
.. _NumPy: http://numpy.org
.. _PyTables: http://pytables.org
.. _NetworkX: http://networkx.github.io
.. _PyDotPlus: https://pydotplus.readthedocs.io/
.. _matplotlib: http://matplotlib.org
.. _ViTables: http://vitables.org
.. _GitHub: http://github.com/arfc/saltproc


Optional Depenendencies:

  #. `matplotlib`_
  #. `ViTables`_



Most of the dependencies are readily available through package managers.
Once all the dependencies are installed, SaltProc can be installed.
Clone the source from the SaltProc repository from `GitHub`_.
Then run the following commands from the directory above cloned repository:

.. code-block:: bash

   git clone https://github.com/arfc/saltproc.git
   cd saltproc/
   python setup.py install --user

Please let us know if you run into trouble.

Cross Section Configuration
---------------------------
SaltProc can use any cross section library that Serpent can. See `this page on the Serpent wiki`_ for more information. 

.. _this page on the Serpent wiki: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries

Testing
-------
The SaltProc test suite has two types of tests: unit tests and regression tests. The unit tests check that the individual functions and classes of the ``saltproc`` module return the correct type of variales and correct values, where applicable. The regression tests run a full saltproc simulation and check the final result with an precalculated result. 
..
   comment: We recommend users and developers use the `JEFF 3.1.2 libarary`_ for running the integration tests. This libaray is available for public download but needs to be processed to be used by Serpent. Check `this discussion page`_ for a guide on how to do this.
To run the tests, execute:

.. code-block:: bash

   pytest saltproc/

from the base directory of SaltProc. If you just want to run the unit tests, execute

.. code-block:: bash

   pytest --ignore saltproc/tests/integration_tests saltproc/

