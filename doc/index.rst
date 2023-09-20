.. Saltproc documentation master file, created by
   sphinx-quickstart on Tue Jul  3 14:26:54 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SaltProc
=========

**SaltProc** is a python package for liquid-fueled nuclear reactor depletion
calculations. It couples directly with depletion-capable transport solvers to enable online reprocessing system modeling in depletion
calculations.

**SaltProc** welcomes your contributions. It already relies on many libraries
in the Scientific Python ecosystem including `openmc`_, `numpy`_, `matplotlib`_,
`networkx`_, and `pydot`_.

.. _openmc: http://openmc.org/
.. _numpy: http://numpy.org
.. _matplotlib: http://matplotlib.org
.. _networkx: http://networkx.github.io
.. _pydot: https://pypi.org/project/pydot/


Documentation
-------------

.. toctree::
   :maxdepth: 1

   overview
   installation
   examples
   releasenotes/index
   methods/index
   userguide/index
   devguide/index
   api/index
   io_formats/index
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

`OpenMC's docpages`_ heavily inspired the structure and format for SaltProc's docpages.

We make our versioned documentation using `sphinx-multiversion`_.

.. _sphinx-multiversion: https://github.com/Holzhaus/sphinx-multiversion
.. _OpenMC's docpages: https://docs.openmc.org/en/stable/index.html
.. _Shablona: https://github.com/uwescience/shablona
.. _eScience Insititute: https://escience.washington.edu

License
-------

SaltProc is available under the open source `BSD 3-clause License`__.

__ https://raw.githubusercontent.com/arfc/saltproc/master/LICENSE
