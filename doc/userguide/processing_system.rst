.. _userguide_processing_system:

Creating Processing System Files
================================
SaltProc uses two different files to represent a processing system:

  - A ``.json`` file defining processing system components

  - A ``.dot`` file linking the processing system components in a graph

.. note::
   An API to write the file defining processing system components is in
   development, but for now it must be written by hand.

Defining Processing System Components
-------------------------------------
The processing system components are defined for each material
that a user want to process. 

.. warning::
   The of the material in the processing system components file **must** match
   the name of the corresponding material in the transport code.

We start with an empty JSON file:

.. code-block:: json

   {

   }

Then add the materials we want to process. For simpilicty, let's only consider
one material, ``fuel``:

.. code-block:: json

   {
       "fuel": {
           "extraction_processes": {}
       } 
   }

Inside the ``fuel`` key, we define our processing system components via the
``extraction_processes`` parameter. There are two components that every model
must have: ``core_outlet`` -- which marks the beginning of the reprocessing
system -- and ``core_inlet`` -- which marks the end of the reprocessing system.
Each process has several fields that must be filled by the user:

``capacity``
  Maximum mass flow rate the process can handle in :math:`g/s`. This parameter is
  currently unused, but could be useful in the future for more physics-based
  implementations of reprocessing.

``efficiency``
  Dictionary mapping element names to extraction efficiencies. These should be empty
  for the ``core_outlet`` and ``core_inlet`` processes since they represetnt the
  beginning and end of the processng system.

``mass_flowrate``
  The mass flowrate of the process in :math:`g/s`.

``volume``
  The volume of the processing component in :math:`cm^3`.

Let's create ``core_inlet`` and ``core_outlet`` first, assuming a capacity
of :math:`9.92 \cdot 10^6` :math:`g/s`, and that the mass flowrate is equal to the
capacity:

.. code-block:: json

   {
       "fuel": {
           "extraction_processes": {
               "core_inlet": {
                   "capacity": 9920000,
                   "efficiency": {},
                   "mass_flowrate": 9920000,
                   "volume": 0
               },
               "core_outlet":
                   "capacity": 9920000,
                   "efficiency": {},
                   "mass_flowrate": 9920000,
                   "volume": 0
           }
       }
   }

Now, let's create three processes that acutally do things: ``gas_separator``,
which removes Kr, Xe, and H from the fuel, ``nickel_filter``, which removes
dissolved metals from the fuel, and ``reductive_extractor``, which removes
fission procducts from the fuel:

.. code-block:: json

   {
       "fuel": {
           "extraction_processes": {
               "core_inlet": {
                   "capacity": 9920000,
                   "efficiency": {},
                   "mass_flowrate": 9920000,
                   "volume": 0
               },
               "core_outlet":
                   "capacity": 9920000,
                   "efficiency": {},
                   "mass_flowrate": 9920000,
                   "volume": 0
               }
               "gas_separator": {
                   "capacity": 9920000,
                   "efficiency": {
                       "Kr": 1,
                       "Xe": 1,
                       "H": 1
                   },
                   "mass_flowrate": 9920000,
                   "volume": 10000000
               },
               "nickel_filter": {
                   "capacity": 9920000,
                   "efficiency": {
                       "Se": 1,
                       "Nb": 1,
                       "Mo": 1,
                       "Tc": 1,
                       "Ru": 1,
                       "Rh": 1,
                       "Pd": 1,
                       "Ag": 1,
                       "Sb": 1,
                       "Te": 1
                   },
                   "mass_flowrate": 9920000,
                   "volume": 11
               },
               "reductive_extractor": {
                   "capacity": 9920000,
                   "efficiency": {
                       "Pa": 1,
                       "Y": 0.8904,
                       "La": 0.8904,
                       "Ce": 0.8904,
                       "Pr": 0.8904,
                       "Nd": 0.8904,
                       "Pm": 0.8904,
                       "Sm": 0.8904,
                       "Gd": 0.8904,
                       "Eu": 0.2,
                       "Rb": 0.032,
                       "Sr": 0.032,
                       "Cs": 0.032,
                       "Ba": 0.032,
                       "Zr": 0.425,
                       "Cd": 0.425,
                       "In": 0.425,
                       "Sn": 0.425,
                       "Br": 0.842,
                       "I": 0.842
                   },
                   "mass_flowrate": 9920000,
                   "volume": 11
           }
       }
   }

In addition to ``extraction_processes``, we can also define ``feeds``, which
are materials added to the reprocessed material after the processing is
performed. ``feeds`` require the following parameters:

``density``
  Density of the material in :math:`g/cm^3`

``volume``
  Volume of the material in :math:`cm^3`

``mass``
  Mass of the material in :math:`g`

``comp``
  A dictionary mapping nuclide names to weight-percent.

In this case, we can add a simple ``fuel_salt`` feed:

.. code-block:: json

   {
       "fuel": {
           "extraction_processes": {
               "core_inlet": {
                   "capacity": 9920000,
                   "efficiency": {},
                   "mass_flowrate": 9920000,
                   "volume": 0
               },
               "core_outlet":
                   "capacity": 9920000,
                   "efficiency": {},
                   "mass_flowrate": 9920000,
                   "volume": 0
               }
               "gas_separator": {
                   "capacity": 9920000,
                   "efficiency": {
                       "Kr": 1,
                       "Xe": 1,
                       "H": 1
                   },
                   "mass_flowrate": 9920000,
                   "volume": 10000000
               },
               "nickel_filter": {
                   "capacity": 9920000,
                   "efficiency": {
                       "Se": 1,
                       "Nb": 1,
                       "Mo": 1,
                       "Tc": 1,
                       "Ru": 1,
                       "Rh": 1,
                       "Pd": 1,
                       "Ag": 1,
                       "Sb": 1,
                       "Te": 1
                   },
                   "mass_flowrate": 9920000,
                   "volume": 11
               },
               "reductive_extractor": {
                   "capacity": 9920000,
                   "efficiency": {
                       "Pa": 1,
                       "Y": 0.8904,
                       "La": 0.8904,
                       "Ce": 0.8904,
                       "Pr": 0.8904,
                       "Nd": 0.8904,
                       "Pm": 0.8904,
                       "Sm": 0.8904,
                       "Gd": 0.8904,
                       "Eu": 0.2,
                       "Rb": 0.032,
                       "Sr": 0.032,
                       "Cs": 0.032,
                       "Ba": 0.032,
                       "Zr": 0.425,
                       "Cd": 0.425,
                       "In": 0.425,
                       "Sn": 0.425,
                       "Br": 0.842,
                       "I": 0.842
                   },
                   "mass_flowrate": 9920000,
                   "volume": 11
           },
           "feeds": {
               "fuel_salt": {
                   "density": 3.35,
                   "volume": 1e8,
                   "mass": 3.35e
                   "comp": {
                       "Li-7": 0.07875361306856505,
                       "Be-9": 0.022558425114333525,
                       "Fl-19": 0.4540013117137259,
                       "Th-232": 0.4446866501033755
                   }
               }
           }
       }
   }

Defining the Processing System Graph
------------------------------------
As mentioned earlier, processing system graphs must be *acyclic directed* graphs.
*Directed* means each edge in the graphs connecting nodes has a specific direction
associated with it, and *acyclic* means there shouldn't be any "loops", that is,
there should be no way to traverse along an edge that takes you back to a node
you already visited.

SaltProc uses the :ref:`networkx` package to process graphs, and this is also
how they should be constructed. We start by importing ``networkx`` and creating
a ``DiGraph``:

.. code-block:: python
   
   import networkx as nx
   system = nx.DiGraph

Next, we need to add nodes to our graph. Each processing system component we defined
previously is a node:

.. warning::
   The names of the nodes **must** match the names of the processing system
   components.

.. code-block:: python

   nodes = ['core_outlet', 'core_inlet', 'gas_separator', 'nickel_filter', 'reductive_extractor']
   for node in nodes:
       system.add_node(node)

Finally, we need to connect the nodes with edges. The graph strucure
of acyclic directed graphs can get fairly complicated, but for this example
our graph is going to be a single point-to-point path:

.. code-block:: python

   edges = [('core_outlet', 'gas_separator'),
            ('gas_separator', 'nickel_filter'),
            ('nickel_filter', 'reductive_extractor'),
            ('reductive_extractor', 'core_inlet')]
   for edge in edges:
       system.add_edge(*edge)


To ensure that our graph is acyclic, we can run

.. code-block:: python

   nx.algorithms.is_directed_acyclic_graph(system)

Finally, we need to export this graph to a ``.dot`` file:

.. code-block:: python

   import networkx.drawing as nxd
   nxd.nx_pydot.write_dot(system, 'processing_graph.dot')
