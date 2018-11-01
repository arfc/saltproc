"""
A python library to manipulate and transform sequences.
The seqtools package contains functions to manipulate sequences
(anything that supports indexing such as lists or arrays).
Its objective is to simplify the execution of pipelines transformations.
Unless otherwise specified, all functions feature on-demand evaluation
which means operations on an item or sequence are only executed when
needed which is convenient for rapid prototyping.
Most function apply 'transparently' over sequence and return objects
that support integer indexing, iteration, slicing, item assignment,
slice based assignment...
The library also feature a robust multihreading/multiprocessing
prefetch routine which hides away the difficulties of concurrent
processing into a simple sequence wrapper.
"""

from __future__ import absolute_import, division, print_function
from .version import __version__  # noqa
from .depcode import *  # noqa
