Contributing
============

Thanks for Your Help!
---------------------

Contributing is so kind of you. In SaltProc, all contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome.

The `GitHub "issues" tab <https://github.com/arfc/saltproc/issues>`__ contains some issues labeled "Difficulty:1-Beginner". Those are open issues that would be a good quick way to get started. Browse them to see if you want to get started on one.

Bug Reports
~~~~~~~~~~~

Is something in the code not working? Consider making a bug report! In particular:

-  Please include a short but detailed, self-contained Python snippet or explanation for reproducing the problem.

-  Explain what the expected behavior was, and what you saw instead.

Feature Requests
~~~~~~~~~~~~~~~~

If you have an idea that could add to or improve SaltProc, and know how to implement it, consider making a Feature Request!

Discussion
~~~~~~~~~~

If you

-  have feedback or a feature idea that aren't concrete/focused enough to go into a Feature Request Issue
-  want to show off cool work you have done with the software

please use our `Discussions page <https://github.com/arfc/saltproc/discussions>`__!

Instructions for setting up a development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The SaltProc is compatible with Python >=3.5. Anaconda is the recommended distribution to use to work on SaltProc; we will assume that if you want to use another distribution or your own set up, you can translate the instructions.

You can download Anaconda at https://www.continuum.io/Downloads for the full install. You can also download a mini Anaconda install for a bare-bones install -- this is good for a build server or if you don't have much space. The mini Anaconda installs are available at https://conda.io/miniconda.html.

Once your Anaconda package is installed and available, create a Python 3.6 environment in Anaconda --

::

   conda create -q -n saltproc-test-environment python=3.6 scipy numpy matplotlib pytest pytables flake8

Each of these commands will take a bit of time -- give it a few minutes to download and install the packages and their dependences. Once complete, switch to each and install additional packages needed to run and test.

Activate the 3.6 environment and install pyne, networkx and pydotplus

::

   source activate saltproc-test-environment
   conda install -c conda-forge pyne networkx pydotplus

Setup Serpent Monte Carlo code environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The SaltProc assumes that Serpent directory is added in ``$PATH`` as follows:

::

   export PATH="/path/to/serpent/executable:$PATH"

Run the tests
^^^^^^^^^^^^^

Tests are automatically detected and run with pytest. Start in the root directory where you have cloned the saltproc repository and run in development environment

::

   source active saltproc-test-environment
   py.test saltproc

Run style tests with flake8
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adherence to style checks in flake8 is encouraged though not strictly enforced. While you should not feel compelled to fix existing failures, please do not add additional flake8 issues.

::

   run flake8 from the root of the pyrk working directory to get all flake8 issues
   run flake8 and provide a filename to just run checks on that file

Pull Requests
^^^^^^^^^^^^^

Please use the provided pull request template. In particular:

-  **Make sure the test suite passes** on your computer. To do so, run ``py.test saltproc`` in the repository directory. At a minimum, you must run the tests reqiuring serpent locally as they are not tested by our CI
-  Describe your feature/change/fix in the release notes (located in ``doc/releasenotes``) for the currently in-development release version. Use the descriptive comments and examples as reference.
-  Please reference relevant Github issues in your commit message using ``GH1234`` or ``#1234``.
-  Changes should be PEP8 compatible `PEP8 <http://www.python.org/dev/peps/pep-0008/>`__.
-  Keep style fixes to a separate commit to make your PR more readable.
-  Docstrings ideally follow the `sphinx autodoc <https://pythonhosted.org/an_example_pypi_project/sphinx.html#function-definitions>`__
-  Write tests.
-  When writing tests, please make sure they are in a ``tests`` directory.
-  When you start working on a PR, start by creating a new branch pointing at the latest commit on github master.
-  The SaltProc copyright policy is detailed in the `LICENSE <https://github.com/arfc/saltproc/blob/master/LICENSE>`__.

More developer docs
~~~~~~~~~~~~~~~~~~~

-  We are working on it.

Meta
~~~~

Note, this contributing file was adapted from the one at the `pandas <https://github.com/pydata/pandas>`__ repo. Thanks pandas!
