.. _methods_reprocessing:

Reprocessing Methods
====================

SaltProc models separations and feeds using three different data structures:

Material flows
--------------
A material flow represents a material with a given
volume :math:`V`, density :math:`\rho`, temperature :math:`T`, and nuclide composition :math:`\mathbf{N}` flowing in or out
of a processing component.
It can also include information such as void fraction. :class:`saltproc.Materialflow`
objects contain the prior mentioned quantities as attributes, as well as
methods to perform the following:

1. Add two :class:`saltproc.Materialflow` objects together

   a. The mass of the sum is :math:`m_{1+2} = m_{1} + m_{2}`

   b. The composition of the sum is :math:`\mathbf{N}_{1+2} = \frac{\mathbf{N}_{1} * m_{1} + \mathbf{N}_{2} * m_{2}}{m_{1} + m_{2}}`

   c. The temperature and density are assumed to be equal to the first :class:`saltproc.Materialflow` object

2. Scale a :class:`saltproc.Materialflow` object by a constant, specifically the mass and volume of the :class:`saltproc.Materialflow` object.
    
:class:`saltproc.Materialflow`. objects are used to store information about
materials in reprocessing as well as materials being fed into the system.

Processes
.........
A process is an abstraction of chemical separation, extraction, or some
other removal. Two processes commonly used in \Gls{msr}s include
extracting metals using gas sparging and filtering. In SaltProc,
:class:`saltproc.Process` objects contain data and functions to perform their
associated processing task. At a minimum, a :class:`saltproc.Process` object includes
the following

1. A mass flow rate, :math:`\dot{m}`, which specifies the mass of fuel salt a process can operate on per unit time
2. An extraction efficiency, :math:`\epsilon`, for target element(s)
3. A method to apply the process on a :class:`saltproc.Materialflow` object

Graphs
......
A graph is a mathematical object that connects *nodes*
with *edges*. More formally,
a graph is a pair of sets, :math:`(V, E)`, where

- :math:`V` is a set whose elements are called nodes
- :math:`E` is a set whose elements are pairs of elements in :math:`V`

A directed graph is a graph in which the elements are ordered pairs of elements
in :math:`V`. This gives the edges a direction. SaltProc uses directed graphs to
model the order and path in which processes operate on materials.
        
Processes and feeds are defined in one JSON input file, and the graph linking
processes is defined in a DOT file. The process graph must be directed and
acyclic in order to work with SaltProc. At runtime,
SaltProc reads this input file to create :class:`saltproc.Process` objects for each item
in the file. Every process file must have at least a :class:`core_outlet` and
:class:`core_inlet` Process.

Material reprocessing
---------------------

Recall that SaltProc uses a *batchwise* reprocessing scheme.
Let :math:`\mathbf{n}(t)^{j}` denote the nuclide mass vector for depletable material
:math:`j` as a function of time. For each depletable material :math:`j`, the depletion
solver numerically integrates the equation

.. math::

    \frac{d\mathbf{n}^{j}(t)}{dt} = \mathbf{A}(\mathbf{n}^{j}(t), t)

from time :math:`i` to time :math:`i+1` to get :math:`\mathbf{n}^{j}(i+1)`, where :math:`A` is the
depletion matrix. This sequence is called a **depletion step**.

Now, let the mass and volume of depletable material :math:`j` be
:math:`m^{j}` and :math:`V^{j}` respectively. Let the mass flow rate of process :math:`p` be
:math:`\dot{m}_{p}`. At the end of each depletion step, SaltProc constructs process
paths from the process graph defined in the DOT file, and sequentially applies
each process :math:`p` in each path :math:`r` to the relevant materials to obtain through
and waste streams for each material. SaltProc tracks the mass and nuclide vector for both through and waste streams. For through
streams, SaltProc also tracks the volume and mass flow rate. For every node
:math:`p\in[0,l]` where :math:`0` represents the core outlet and :math:`l` represents the core
inlet, in the path :math:`r`, for the through streams we have

.. math::

    \mathbf{n}^{j}_{\text{through, }p,r} = \mathbf{n}^{j}_{\text{through, }p-1,r} (1 - \pmb{\epsilon}^{j}_{p,r})

.. math::

    m^{j}_{\text{through, } p,r} = \alpha_{p} m^{j}_{\text{through, }p-1,r} - m^{j}_{\text{waste, }p,r}

.. math::

    V^{j}_{\text{through, }p,r} = \alpha_{p}V^{j}_{\text{through, }p-1,r}

where 

.. math::

    \alpha_{p,r} = \frac{\dot{m}_{p,r}}{\dot{m}_{\text{outlet}}}

and the initial conditions are 

.. math::

    \mathbf{n}^{j}_{\text{through, }0,r} = \mathbf{n}^{j}(i+1)

.. math::

    m^{j}_{\text{through, }0,r} = \rho^{j}(i+1)V^{j}(i+1)

.. math::

    V^{j}_{\text{through, }0,r} = V^{j}(i+1)

Similarly, for the waste streams, we have

.. math::

    \mathbf{n}^{j}_{\text{waste, }p,r} = \mathbf{n}^{j}_{\text{through, }p-1,r} \cdot \pmb{\epsilon}^{j}_{p,r}

.. math::

    m^{j}_{\text{waste, }p,r} = \alpha_{p,r} m^{j}_{\text{through, }p-1,r} \langle\mathbf{1},\mathbf{n}^{j}_{\text{waste, }p,r}\rangle


SaltProc does not currently track the volume and mass flow rate of waste streams.
In practice, since it is extremely resource intensive to separate individual
isotopes, SaltProc only allows extraction efficiencies to be defined for
elements. Additionally, any chemical processing would only act on elements, so there is little point in having isotope specific extration efficiencies. So, for any isotope :math:`a` of xenon,
:math:`\epsilon_{\ce{^{a}Xe}} = \epsilon_{\ce{^{a^{\prime}}Xe}}`  where
:math:`a^{\prime} \in \text{isotopes of Xe}`

After the recursive computation, SaltProc sums through and waste streams over all
paths to get the total through stream at the inlet, and the total waste stream at
the inlet which represents all material removed during reprocessing. In practice,
we are working with nuclide mass fractions, not total masses, so in the program
there is an expansion and then normalization of the vectors:

.. math::

    \mathbf{n}^{j}_\text{through, inlet, net} = \frac{\sum_{r} m^{j}_{\text{through, inlet, }r} \mathbf{n}^{j}_{\text{through, inlet, }r}}{\sum_{r} m^{j}_{\text{through, inlet, }r}}

.. math::

    \mathbf{n}^{j}_{\text{waste, inlet, net}} = \frac{\sum_{r} m^{j}_{\text{waste, inlet, }r} \mathbf{n}^{j}_{\text{waste, inlet, }r}}{m^{j}_{\text{waste, inlet, }r}}

Before running the next depletion step, for any material that has an associated
feed material defined, SaltProc will add an amount of the feed material
equivalent to the removed mass so that the mass of fuel salt undergoing depletion
remains constant. For feed :math:`j'` corresponding to material :math:`j`, we have

.. math::

    \mathbf{n}^{j}_\text{filled} = \frac{m^{j}_{\text{through, }l}\mathbf{n}^{j}_\text{through, inlet, net} +  m^{j}_{\text{removed}}\mathbf{n}^{j'}}{m^{j}_{\text{through, }0}}

where 

.. math::

    m^{j}_\text{removed} = m^{j}_{\text{through, }0} - m^{j}_{\text{through, }l}
