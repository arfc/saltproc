.. _userguide_input:

Creating a SaltProc input file
==============================

The SaltProc input file passes three categories of information to the program:

1. Paths to files that describe the reprocessing system
2. Paths to template files for the transport code.
3. Depletion settings

In the following sections, we will create an example SaltProc input file, and
explain the purpose for each input variable. For a more detailed breakdown of
the inputs, check the :ref:`io_formats_input_files` page.

Creating a JSON file
--------------------
JSON files themselves are not that complicated. They consist of key-value pairs,
much like a dictionary in Python. The entire JSON files needs to be wrapped with curly brackets, so we start our file like so:

.. code-block:: json

   {

   }


Base paremters
-------------------
There are two required base parameters: :ref:`proc_input_file_property`, a path to the file
that defines processes, and :ref:`dot_input_file_property`, a path to the file that defines
the process graph. We will learn how to create these files in the next chapter,
but for now we just need to specify a path. We recommend storing all the input
files in the same directory, but this is not requried.

Let's name our process file `processes.json` and the process graph file `graph.dot`:

.. code-block:: json

   {
       "proc_input_file": "processes.json",
       "dot_input_file": "graph.dot"
   }


Transport code parameters
-------------------------
As explained in :ref:`methods_coupling`, SaltProc uses template files provided
by the user to create runtime files that are used as inputs to the transport
code for each depletion step. The :ref:`depcode_property` setting in the
SaltProc input file store paths to these template files, as well as other
settings. The only two input parameters that have the same format for
different transport codes are :ref:`codename_property` and
:ref:`geo_file_paths_property`. ``codename`` is a string that indicates the
transport code you are using. Accepted values are lowercased versions of the
supported transport code (e.g. "serpent", "openmc"). ``geo_file_paths`` is a
list of paths to geometry files [#f1]_. At least one path to a geometry file must
be given, and for the purposes of this guide this is sufficient.

Let's briefly break down the minimum requirements for each supported transport
code.

Serpent2
~~~~~~~~
Only two additional parameters are needed for Serpent2 coupling. The first is 
:ref:`serpent_template_input_file_path_property`, which is a path to a template
input file. We describe the structure of this file in :ref:`userguide_templates_serpent`.
The second is :ref:`zaid_convention_property`, which is a string that tells SaltProc what
convention to use for the ZAIDs of metastable isotopes. By default, SaltProc
uses the ``mcnp`` convention. 
Let's
assume that we name our template input file `template.serpent`:

.. code-block:: json

   {
       "proc_input_file": "processes.json",
       "dot_input_file": "graph.dot",
       "depcode": {
           "codename": "serpent":
           "geo_file_paths": ["geometry.ini"],
           "template_input_file_path": "template.serpent"
       }
   }


OpenMC
~~~~~~
The OpenMC inputs are more complicated. There are two reasons for this:

1. OpenMC uses separate input files for material, geometry, settings, and tally parameters, and uses strict naming for these input files.
2. Configuring OpenMC's depletion capabilities must be done via the Python API, so what normally would be handled in the template input file must be handled directly in the SaltProc input file.

Fortunately, SaltProc doesn't require users to touch these setting at all if
they want to use the default options. Users interested in configuring their
OpenMC depletion settings should advise the `deplete module API`_ as well as the
`user guide section on depletion`_ to familiarize themselves with the various
options, then look at the section on...

The ``depcode`` paramter for OpenMC also has the
:ref:`openmc_template_input_file_path_property` parameter, except it is an
object that in turn requires two file paths:
``materials`` for the materials file, and ``settings`` for the settings file.
There is an additonal required parameter, :ref:`openmc_chain_file_path_property`
which is a path to an OpenMC depletion chain file. Suppose we prepend
``template_`` to the names of our OpenMC input files:

.. code-block:: json

   {
       "proc_input_file": "processes.json",
       "dot_input_file": "graph.dot",
       "depcode": {
           "codename": "openmc":
           "geo_file_paths": ["geometry.xml"],
           "template_input_file_path": {
               "materials": "template_materials.xml",
               "settings": "template_settings.xml"
           },
           "chain_file_path": "chain_simple.xml"
       }
   }


.. _deplete module API: https://docs.openmc.org/en/stable/pythonapi/deplete.html
.. _user guide section on depletion: https://docs.openmc.org/en/stable/usersguide/depletion.html


Simulation parameters
---------------------
SaltProc allows some degree of control over how the simulation behaves. These are not relevant...

Depletion step parameters
-------------------------
In general, depletion parameters other than the defualts (e.g. timestepper
method, solver used for the Bateman equations, normalization, etc.) should be
set in the template input file when possible. The rationale for this is that
these settings have more to do with the internal depletion calculations of the
transport code than they do with SaltProc execution. The obvious exception to
this is the delpletion step settings. 

SaltProc has three...



.. rubric:: Footnotes

.. [#f1] As explained in :ref:`methods_geometry_switching`, SaltProc allows a user to provide multiple geometry configurations that are switched to sequentially if that option is enabled and :math:`k_\text{eff}` drops below 1
