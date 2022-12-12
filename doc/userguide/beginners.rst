.. _userguide_beginners:

A Beginner's Guide to SaltProc
==============================

What does SaltProc do?
----------------------
In a nutshell, SaltProc is an interface code for transport solvers with
depletion capabilites that simulates chemical reprocessing of fuel. In general,
there are two ways to simulate chemical fuel reprocessing: continuous, and
batchwise. As an interface code, SaltProc uses a batchwise approach to simulate
chemical fuel reprocessing. See :ref:`methods_reprocessing` for further details on
how this works.

How does it work?
-----------------
SaltProc uses abstraction to represent chemical reprocessing components --
hereon referred to as *processes*. These processes are linked together using a
graph. SaltProc routes depleted materials through this graph and applies the
respecive process at each node. See :ref:`methods_reprocessing` for a more in-depth
breakdown of this design.

What do I need to know?
-----------------------
If you are starting to work with SaltProc, there are a few things you should be familiar with:

- You should be comfortable with working in a command line environment.
- You should be familiar with at least one of the supported transport solvers.
  See :ref:`the list of supported codes <supported_codes>` for a list of currently supported transport solvers.
