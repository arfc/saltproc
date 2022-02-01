.. Saltproc documentation master file, created by
   sphinx-quickstart on Tue Jul  3 14:26:54 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SaltProc
=========

**SaltProc** is a python package for liquid-fueled nuclear reactor depletion
calculations. It couples directly with the Serpent 2 Monte Carlo depletion
software to enable online reprocessing system modeling in depletion
calculation.

**SaltProc** welcomes your contributions. It already relies on many libraries
in the Scientific Python ecosystem including `pyne`_, `numpy`_, `matplotlib`_,
`networkx`_, and `pydotplus`_.

.. _pyne: http://pyne.io/
.. _numpy: http://numpy.org
.. _matplotlib: http://matplotlib.org
.. _networkx: http://networkx.github.io
.. _pydotplus: https://pydotplus.readthedocs.io/


Documentation
-------------

.. toctree::
   :maxdepth: 1

   overview
   installation
   examples
   src/index
   releasenotes/index
   devguive/index
   How to cite <https://github.com/arfc/saltproc/blob/master/CITATION.md>

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



Citation
--------

Up-to-date information about citing SaltProc can be found within the `citation`_
file.

.. _citation: https://github.com/arfc/saltproc/blob/master/CITATION.md


Get in touch
------------

- Please report bugs, suggest feature ideas, and browse the source code `on GitHub`_.
- There, new contributors can also find `a guide to contributing`_.
- Good start point for new contributors is `current open issues`_.

.. _a guide to contributing: https://github.com/arfc/saltproc/blob/master/CONTRIBUTING.md
.. _current open issues: https://github.com/arfc/saltproc/issues?q=is%3Aopen+is%3Aissue
.. _on GitHub: http://github.com/arfc/saltproc

Acknowledgment
--------------

SaltProc uses `Shablona`_ template which is universal solution for small
scientific python projects developed at University of Washington `eScience Insititute`_.

.. _Shablona: https://github.com/uwescience/shablona
.. _eScience Insititute: https://escience.washington.edu

License
-------

SaltProc is available under the open source `BSD 3-clause License`__.

__ https://raw.githubusercontent.com/arfc/saltproc/master/LICENSE
