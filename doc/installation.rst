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
SaltProc can use any cross section library that Serpent can. See `this page on the Serpent wiki`_ for information on how to configure the libraries. 

.. _this page on the Serpent wiki: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries

Testing
-------
The SaltProc test suite has two types of tests: unit tests and regression tests.
The unit tests check that the individual functions and classes of the ``saltproc``
module return the correct type of variables and correct values, where applicable. 
The regression tests run a full SaltProc simulation and check the final result
with a precalculated result. 
The integration tests require the `JEFF 3.1.2 cross section library`_. 
The publicly available versions of this library cannot be used with Serpent right
out of the box due to `Serpent's notation for isomeric states`_. The scripts in
``scripts/xsdata`` download and perform all the necessary processing on this
library for use in Serpent 2. We recommend using them for your convenience. 
See the `README`_ for more information.

.. _Serpent's notation for isomeric states: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries
.. _JEFF 3.1.2 cross section library: https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/JEFF312/
.. _README: https://github.com/arfc/saltproc/blob/master/scripts/README.md

To run the tests, execute:

.. code-block:: bash

   pytest saltproc/

from the root directory of SaltProc. If you just want to run the unit tests, execute

.. code-block:: bash

   pytest --ignore saltproc/tests/integration_tests saltproc/

