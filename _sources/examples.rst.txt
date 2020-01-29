Examples
=========

A number of examples are present in the [examples
directory](https://github.com/arfc/saltproc/tree/master/examples)
provided with the source code.

Transatomic Power Molten Salt Reactor example can be run with:


.. code-block:: bash

   cd /path/to/saltproc
   python saltproc -i examples/tap_main.json


In the example above, ``path/to/saltproc`` is, of course, the path to the main
saltproc directory, containing ``setup.py``. The ``tap_main.json`` is the main
Saltproc input file, which contains paths to Serpent input file
(``tap.serpent``), DOT-file with reprocessing scheme (``tap.dot``), and
reprocessing system components detailed description (``tap_objects.json``).
